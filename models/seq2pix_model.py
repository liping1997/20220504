import torch
from .base_model import BaseModel
from . import networks
import itertools
from .losses import PerceptualLoss
import cv2
import numpy as np
import torchvision.transforms as transforms
from util.util import tensor2im


class Seq2PixModel(BaseModel):


    @staticmethod
    def modify_commandline_options(parser, is_train=True):

        # changing the default values to match the pix2pix paper (https://phillipi.github.io/pix2pix/)
        parser.set_defaults(norm='batch', netG='resnet_9blocks', dataset_mode='aligned')
        if is_train:
            parser.set_defaults(pool_size=0, gan_mode='vanilla')
            parser.add_argument('--lambda_L1', type=float, default=100.0, help='weight for L1 loss')
            parser.add_argument('--lambda_P', type=float, default=0.01, help='weight for perceptual loss')
        return parser

    def __init__(self, opt):

        BaseModel.__init__(self, opt)
        # specify the training losses you want to print out. The training/train scripts will call <BaseModel.get_current_losses>
        self.loss_names = ['G0_GAN', 'G0_L1', 'G0_perceptual', 'D0_real', 'D0_fake',
                           'G1_GAN', 'G1_L1', 'G1_perceptual','D0_real', 'D0_fake',
                           'G2_GAN', 'G2_L1', 'G2_perceptual', 'D0_real', 'D0_fake',]
        # specify the images you want to save/display. The training/train scripts will call <BaseModel.get_current_visuals>
        self.visual_names = ['real_A', 'fake_B0', 'real_B0', 'fake_B1', 'real_B1', 'fake_B2', 'real_B2']
        # self.visual_names = ['real_A', 'fake_B0', 'real_B0']
        # self.visual_names = ['real_A', 'real_B1', 'fake_B1']
        # self.visual_names = ['real_A', 'fake_B2', 'real_B2']
        # specify the models you want to save to the disk. The training/train scripts will call <BaseModel.save_networks> and <BaseModel.load_networks>
        if self.isTrain:
            self.model_names = ['G0', 'D0', 'G1',  'G2','G']
        else:  # during train time, only load G
            self.model_names = ['G0', 'G1', 'G2','G']
        # define networks (both generator and discriminator)
        self.netG=networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netg1, opt.is_second_train, opt.norm)
        self.netG0 = networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netg2, opt.is_second_train, opt.norm,
                                       not opt.no_dropout, False, opt.init_type, opt.init_gain, self.gpu_ids)
        self.netG1 = networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netg2, opt.is_second_train, opt.norm,
                                       not opt.no_dropout, True, opt.init_type, opt.init_gain, self.gpu_ids)

        self.netG2 = networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netg2, opt.is_second_train, opt.norm,
                                       not opt.no_dropout, True, opt.init_type, opt.init_gain, self.gpu_ids)

        if self.isTrain:  # define a discriminator; conditional GANs need to take both input and output images; Therefore, #channels for D is input_nc + output_nc
            self.netD0 = networks.define_D(opt.input_nc + opt.output_nc, opt.ndf, opt.netD, opt.is_second_train,
                                           opt.n_layers_D, opt.norm, opt.init_type, opt.init_gain, self.gpu_ids)

        if self.isTrain:
            # define loss functions
            self.criterionGAN = networks.GANLoss(opt.gan_mode).to(self.device)
            self.criterionL1 = torch.nn.L1Loss()
            self.perceptual_loss = PerceptualLoss(torch.nn.MSELoss())
            # self.saliency_loss = torch.nn.MSELoss()
            # initialize optimizers; schedulers will be automatically created by function <BaseModel.setup>.
            self.optimizer_G1 = torch.optim.Adam(
                itertools.chain(self.netG.parameters(),self.netG0.parameters()), lr=opt.lr,
                betas=(opt.beta1, 0.999))
            self.optimizer_G2 = torch.optim.Adam(
                itertools.chain(self.netG.parameters(), self.netG1.parameters()), lr=opt.lr,
                betas=(opt.beta1, 0.999))
            self.optimizer_G3 = torch.optim.Adam(
                itertools.chain(self.netG.parameters(), self.netG2.parameters()), lr=opt.lr,
                betas=(opt.beta1, 0.999))
            self.optimizer_D = torch.optim.Adam(
                itertools.chain(self.netD0.parameters()), lr=opt.lr,
                betas=(opt.beta1, 0.999))
            self.optimizers.append(self.optimizer_G1)
            self.optimizers.append(self.optimizer_G2)
            self.optimizers.append(self.optimizer_G3)
            self.optimizers.append(self.optimizer_D)
        self.pic_num=0
        # self.pic_num = 1
        # self.pic_num = 2

    def set_input(self, input):

        AtoB = self.opt.direction == 'AtoB'
        self.real_A = input['A' if AtoB else 'B'].to(self.device)
        self.real_B0 = input['B0' if AtoB else 'A'].to(self.device)
        self.real_B1 = input['B1' if AtoB else 'A'].to(self.device)
        self.real_B2 = input['B2' if AtoB else 'A'].to(self.device)
        self.image_paths = input['A_paths' if AtoB else 'B0_paths']

    def forward(self):
        self.x=self.netG(self.real_A)
        if self.pic_num%3==0:
            self.fake_B0 = self.netG0(self.x)  # G(A)
        elif self.pic_num % 3 == 1:
            self.fake_B1 = self.netG1(self.x)
        elif self.pic_num % 3 == 2:
            self.fake_B2 = self.netG2(self.x)

    def backward_D_basic(self, netD, real_A, fake_B, real_B):
        # Fake; stop backprop to the generator by detaching fake_B
        fake_AB = torch.cat((real_A, fake_B),
                            1)  # we use conditional GANs; we need to feed both input and output to the discriminator
        pred_fake = netD(fake_AB.detach())
        loss_D_fake = self.criterionGAN(pred_fake, False)
        # Real
        real_AB = torch.cat((real_A, real_B), 1)
        pred_real = netD(real_AB)
        loss_D_real = self.criterionGAN(pred_real, True)
        return loss_D_fake, loss_D_real

    def backward_D(self):
        if  self.pic_num%3==0:
            self.loss_D0_fake, self.loss_D0_real = self.backward_D_basic(self.netD0, self.real_A, self.fake_B0,
                                                                self.real_B0)
            self.loss_D = (self.loss_D0_fake + self.loss_D0_real) * 0.5
            self.loss_D.backward()
        elif self.pic_num%3==1:
            self.loss_D1_fake, self.loss_D1_real = self.backward_D_basic(self.netD0, self.real_A, self.fake_B1,
                                                                     self.real_B1)
            self.loss_D = (self.loss_D1_fake + self.loss_D1_real) * 0.5
            self.loss_D.backward()
        elif self.pic_num%3==2:
            self.loss_D2_fake, self.loss_D2_real = self.backward_D_basic(self.netD0, self.real_A, self.fake_B2,
                                                                     self.real_B2)
            self.loss_D = (self.loss_D2_fake + self.loss_D2_real) * 0.5
            self.loss_D.backward()


    def backward_G_basic(self, netD, real_A, fake_B, real_B):
        """Calculate GAN and L1 loss for the generator"""
        # First, G(A) should fake the discriminator
        fake_AB = torch.cat((real_A, fake_B), 1)
        pred_fake = netD(fake_AB)
        loss_G_GAN = self.criterionGAN(pred_fake, True)
        # Second, G(A) = B
        loss_G_L1 = self.criterionL1(fake_B, real_B) * self.opt.lambda_L1
        loss_G_perceptual = self.perceptual_loss.get_loss(fake_B, real_B) * self.opt.lambda_P
        return loss_G_GAN, loss_G_L1, loss_G_perceptual

    def backward_G(self):
        """Calculate GAN and L1 loss for the generator"""
        # self.loss_G0_GAN, self.loss_G0_L1, self.loss_G0_perceptual = self.backward_G_basic(self.netD0, self.real_A, self.fake_B0, self.real_B0)
        # self.loss_G1_GAN, self.loss_G1_L1, self.loss_G1_perceptual = self.backward_G_basic(self.netD1, self.real_A, self.fake_B1, self.real_B1)
        # self.loss_G2_GAN, self.loss_G2_L1, self.loss_G2_perceptual = self.backward_G_basic(self.netD2, self.real_A, self.fake_B2, self.real_B2)
        if self.pic_num%3==0:
            self.loss_G0_GAN, self.loss_G0_L1, self.loss_G0_perceptual = self.backward_G_basic(self.netD0, self.real_A,
                                                                                           self.fake_B0, self.real_B0)
            self.loss_G = self.loss_G0_GAN + self.loss_G0_L1 + self.loss_G0_perceptual
            self.loss_G.backward()

        if self.pic_num%3==1:
            self.loss_G1_GAN, self.loss_G1_L1, self.loss_G1_perceptual = self.backward_G_basic(self.netD0, self.real_A,
                                                                                           self.fake_B1, self.real_B1)
            self.loss_G = self.loss_G1_GAN + self.loss_G1_L1 + self.loss_G1_perceptual
            self.loss_G.backward()
        if self.pic_num%3==2:
            self.loss_G2_GAN, self.loss_G2_L1, self.loss_G2_perceptual = self.backward_G_basic(self.netD0, self.real_A,
                                                                                           self.fake_B2, self.real_B2)
            self.loss_G = self.loss_G2_GAN + self.loss_G2_L1 + self.loss_G2_perceptual
            self.loss_G.backward()
        # combine loss and calculate gradients
        # self.loss_G = self.loss_G0_GAN + self.loss_G0_L1 + self.loss_G0_perceptual + self.loss_G0_saliency + self.loss_G1_GAN + self.loss_G1_L1 + self.loss_G1_perceptual + self.loss_G1_saliency + self.loss_G2_GAN + self.loss_G2_L1 + self.loss_G2_perceptual + self.loss_G2_saliency


    def optimize_parameters(self):
        for i in range(3):
            self.forward()  # compute fake images: G(A)
            # update D
            self.set_requires_grad([self.netD0], True)  # enable backprop for D
            self.optimizer_D.zero_grad()  # set D's gradients to zero
            self.backward_D()  # calculate gradients for D
            # self.backward_D1()
            self.optimizer_D.step()  # update D's weights
            # update G
            self.set_requires_grad([self.netD0], False)  # D requires no gradients when optimizing G
            if self.pic_num%3==0:
                self.optimizer_G1.zero_grad()
                # set G's gradients to zero
                self.backward_G()  # calculate graidents for G
                self.optimizer_G1.step()  # udpate G's weights

            if self.pic_num%3==1:
                self.optimizer_G2.zero_grad()  # set G's gradients to zero
                self.backward_G()  # calculate graidents for G
                self.optimizer_G2.step()  # udpate G's weights
            if self.pic_num%3==2:
                self.optimizer_G3.zero_grad()  # set G's gradients to zero
                self.backward_G()  # calculate graidents for G
                self.optimizer_G3.step()  # udpate G's weights
            self.pic_num=self.pic_num+1



