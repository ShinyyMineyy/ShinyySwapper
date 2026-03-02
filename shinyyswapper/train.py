import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
import insightface
from insightface.app import FaceAnalysis
import lpips
from pathlib import Path
import json
from tqdm import tqdm
from model import Generator, MultiScaleDiscriminator
from dataset import FaceSwapDataset

class Trainer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Models
        self.G = Generator().to(self.device)
        self.D = MultiScaleDiscriminator().to(self.device)
        
        # Face recognition for identity loss
        self.face_app = FaceAnalysis(providers=['CUDAExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(256, 256))
        
        # Perceptual loss
        self.lpips_loss = lpips.LPIPS(net='vgg').to(self.device)
        
        # Optimizers
        self.opt_G = optim.Adam(self.G.parameters(), lr=config['lr'], betas=(0.5, 0.999))
        self.opt_D = optim.Adam(self.D.parameters(), lr=config['lr'], betas=(0.5, 0.999))
        
        # Mixed precision
        self.scaler = GradScaler()
        
        # Dataset
        self.dataset = FaceSwapDataset(config['data_root'], config['img_size'])
        self.loader = DataLoader(self.dataset, batch_size=config['batch_size'], 
                                shuffle=True, num_workers=2, pin_memory=True)
        
        self.start_epoch = 0
        self.global_step = 0
    
    def extract_identity(self, img):
        img_np = ((img.permute(0, 2, 3, 1).cpu().numpy() + 1) * 127.5).astype('uint8')
        embeddings = []
        for i in range(img_np.shape[0]):
            faces = self.face_app.get(img_np[i])
            if faces:
                embeddings.append(torch.FloatTensor(faces[0].embedding))
            else:
                embeddings.append(torch.zeros(512))
        return torch.stack(embeddings).to(self.device)
    
    def train_step(self, batch):
        target = batch['target'].to(self.device)
        source = batch['source'].to(self.device)
        
        # Extract identity
        source_id = self.extract_identity(source)
        
        # Train Discriminator
        self.opt_D.zero_grad()
        with autocast():
            fake, occlusion_mask = self.G(target, source_id)
            
            real_preds = self.D(target)
            fake_preds = self.D(fake.detach())
            
            d_loss = 0
            for real_pred, fake_pred in zip(real_preds, fake_preds):
                d_loss += torch.mean((real_pred - 1) ** 2) + torch.mean(fake_pred ** 2)
        
        self.scaler.scale(d_loss).backward()
        self.scaler.step(self.opt_D)
        
        # Train Generator
        self.opt_G.zero_grad()
        with autocast():
            fake, occlusion_mask = self.G(target, source_id)
            fake_preds = self.D(fake)
            
            # Adversarial loss
            g_adv_loss = sum([torch.mean((pred - 1) ** 2) for pred in fake_preds])
            
            # Identity loss (only on visible face regions)
            fake_id = self.extract_identity(fake)
            id_loss = torch.mean((fake_id - source_id) ** 2)
            
            # Perceptual loss
            perc_loss = self.lpips_loss(fake, target).mean()
            
            # Reconstruction loss (preserve occluded regions like hair/glasses)
            recon_loss = nn.L1Loss()(fake * (1 - occlusion_mask), target * (1 - occlusion_mask))
            
            # Occlusion consistency (hair/glasses should stay same)
            occlusion_loss = torch.mean(torch.abs(occlusion_mask - 0.5))  # Encourage clear separation
            
            g_loss = g_adv_loss + id_loss * 15 + perc_loss * 5 + recon_loss * 8 + occlusion_loss * 2
        
        self.scaler.scale(g_loss).backward()
        self.scaler.step(self.opt_G)
        self.scaler.update()
        
        return {'d_loss': d_loss.item(), 'g_loss': g_loss.item(), 
                'id_loss': id_loss.item(), 'perc_loss': perc_loss.item(),
                'occlusion_loss': occlusion_loss.item()}
    
    def save_checkpoint(self, epoch):
        checkpoint = {
            'epoch': epoch,
            'global_step': self.global_step,
            'G_state': self.G.state_dict(),
            'D_state': self.D.state_dict(),
            'opt_G_state': self.opt_G.state_dict(),
            'opt_D_state': self.opt_D.state_dict(),
            'scaler_state': self.scaler.state_dict()
        }
        save_path = Path(self.config['checkpoint_dir']) / f'checkpoint_epoch_{epoch}.pt'
        torch.save(checkpoint, save_path)
        print(f"Saved checkpoint: {save_path}")
    
    def load_checkpoint(self, path):
        checkpoint = torch.load(path, map_location=self.device)
        self.G.load_state_dict(checkpoint['G_state'])
        self.D.load_state_dict(checkpoint['D_state'])
        self.opt_G.load_state_dict(checkpoint['opt_G_state'])
        self.opt_D.load_state_dict(checkpoint['opt_D_state'])
        self.scaler.load_state_dict(checkpoint['scaler_state'])
        self.start_epoch = checkpoint['epoch'] + 1
        self.global_step = checkpoint['global_step']
        print(f"Loaded checkpoint from epoch {checkpoint['epoch']}")
    
    def train(self):
        for epoch in range(self.start_epoch, self.config['epochs']):
            pbar = tqdm(self.loader, desc=f"Epoch {epoch}")
            for batch in pbar:
                losses = self.train_step(batch)
                self.global_step += 1
                
                pbar.set_postfix(losses)
                
                if self.global_step % self.config['save_interval'] == 0:
                    self.save_checkpoint(epoch)
            
            self.save_checkpoint(epoch)

if __name__ == '__main__':
    config = {
        'data_root': '/content/drive/MyDrive/shinyyswapper_data',
        'checkpoint_dir': '/content/drive/MyDrive/shinyyswapper_checkpoints',
        'img_size': 512,  # Higher resolution for full head
        'batch_size': 4,   # Reduced for 512x512
        'lr': 0.0001,
        'epochs': 100,
        'save_interval': 500
    }
    
    Path(config['checkpoint_dir']).mkdir(parents=True, exist_ok=True)
    
    trainer = Trainer(config)
    
    # Resume from checkpoint if exists
    checkpoints = list(Path(config['checkpoint_dir']).glob('*.pt'))
    if checkpoints:
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        trainer.load_checkpoint(latest)
    
    trainer.train()
