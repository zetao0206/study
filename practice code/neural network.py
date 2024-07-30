from torch import nn,save,load
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

train = datasets.MNIST(root="data", download=True, train=True, transform=ToTensor())
test = datasets.MNIST(root="data", download=True, train=False, transform=ToTensor())

train_set = DataLoader(train, batch_size=64, shuffle=True)
test_set = DataLoader(test, batch_size=64, shuffle=True)

class imageClassifier(nn.Module):
    def __init__(self):
        super().__init__() 
        self.model = nn.Sequential(
            nn.Conv2d(1,64,(3,3)),
            nn.ReLU(),
            nn.Conv2d(64,64,(3,3)),
            nn.ReLU(),
            nn.Conv2d(64,64,(3,3)),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64*22*22, 10)
        )

    def forward(self, x):
        return self.model(x)

device = "cuda"
model = imageClassifier().to(device)
opt = Adam(model.parameters(), lr = 1e-3)
loss_fn = nn.CrossEntropyLoss()

if __name__ == "__main__":
    for epoch in range(10):
        for batch in train_set:
            x,y = batch
            x, y = x.to(device), y.to(device)
            yh = model(x)
            loss = loss_fn(yh, y)

            opt.zero_grad()
            loss.backward()
            opt.step()
        print(f'Epoch:{epoch} loss is {loss.item()}') 
    
with open('model_state.pt', 'wb') as f:
    save(model.state_dict(),f)



