import torch
import torch.nn as nn
import torch.nn.functional as F

class ResBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(dim, dim, 3, 1, 1), nn.InstanceNorm2d(dim), nn.ReLU(True),
            nn.Conv2d(dim, dim, 3, 1, 1), nn.InstanceNorm2d(dim))
    
    def forward(self, x):
        return x + self.conv(x)

class Generator(nn.Module):
    """Occlusion-aware generator: Preserves hair, glasses, hands covering face"""
    def __init__(self, img_size=512):
        super().__init__()
        # Encoder
        self.enc = nn.Sequential(
            nn.Conv2d(3, 64, 7, 1, 3), nn.InstanceNorm2d(64), nn.ReLU(True),
            nn.Conv2d(64, 128, 4, 2, 1), nn.InstanceNorm2d(128), nn.ReLU(True),
            nn.Conv2d(128, 256, 4, 2, 1), nn.InstanceNorm2d(256), nn.ReLU(True),
            nn.Conv2d(256, 512, 4, 2, 1), nn.InstanceNorm2d(512), nn.ReLU(True),
            nn.Conv2d(512, 512, 4, 2, 1), nn.InstanceNorm2d(512), nn.ReLU(True))
        
        # Occlusion mask predictor (detects hair, glasses, hands)
        self.occlusion_net = nn.Sequential(
            nn.Conv2d(512, 256, 3, 1, 1), nn.ReLU(True),
            nn.Conv2d(256, 128, 3, 1, 1), nn.ReLU(True),
            nn.Conv2d(128, 1, 1), nn.Sigmoid())
        
        # Identity embedding
        self.id_enc = nn.Sequential(
            nn.Linear(512, 1024), nn.ReLU(True),
            nn.Linear(1024, 512))
        
        # Residual blocks (16 for complex features)
        self.res_blocks = nn.ModuleList([ResBlock(512) for _ in range(16)])
        
        # Spatial attention
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(512, 256, 1), nn.ReLU(True),
            nn.Conv2d(256, 512, 1), nn.Sigmoid())
        
        # Decoder
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(512, 512, 4, 2, 1), nn.InstanceNorm2d(512), nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, 4, 2, 1), nn.InstanceNorm2d(256), nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1), nn.InstanceNorm2d(128), nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.InstanceNorm2d(64), nn.ReLU(True),
            nn.Conv2d(64, 3, 7, 1, 3), nn.Tanh())
        
        # Refinement for boundaries
        self.refine = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1), nn.ReLU(True),
            nn.Conv2d(64, 64, 3, 1, 1), nn.ReLU(True),
            nn.Conv2d(64, 3, 3, 1, 1), nn.Tanh())
    
    def forward(self, target_img, source_id):
        # Encode
        x = self.enc(target_img)
        
        # Predict occlusion mask
        occlusion_mask = self.occlusion_net(x)
        occlusion_mask = F.interpolate(occlusion_mask, size=target_img.shape[2:], mode='bilinear')
        
        # Identity embedding
        id_emb = self.id_enc(source_id).unsqueeze(-1).unsqueeze(-1)
        
        # Apply identity with attention
        for block in self.res_blocks:
            x = block(x)
            attn = self.spatial_attention(x)
            x = x + id_emb * attn * 0.2
        
        # Decode
        swapped = self.dec(x)
        swapped = swapped + self.refine(swapped) * 0.3
        
        # Blend: Keep hair/glasses from target, only swap visible face
        result = swapped * occlusion_mask + target_img * (1 - occlusion_mask)
        
        return result, occlusion_mask

class MultiScaleDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.discriminators = nn.ModuleList([
            self._make_disc() for _ in range(3)])
        self.downsample = nn.AvgPool2d(3, 2, 1, count_include_pad=False)
    
    def _make_disc(self):
        return nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1), nn.LeakyReLU(0.2, True),
            nn.Conv2d(64, 128, 4, 2, 1), nn.InstanceNorm2d(128), nn.LeakyReLU(0.2, True),
            nn.Conv2d(128, 256, 4, 2, 1), nn.InstanceNorm2d(256), nn.LeakyReLU(0.2, True),
            nn.Conv2d(256, 512, 4, 1, 1), nn.InstanceNorm2d(512), nn.LeakyReLU(0.2, True),
            nn.Conv2d(512, 1, 4, 1, 1))
    
    def forward(self, x):
        results = []
        for disc in self.discriminators:
            results.append(disc(x))
            x = self.downsample(x)
        return results
