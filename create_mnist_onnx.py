import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

# Simple MNIST model
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(
            nn.Linear(28*28, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        x = self.flatten(x)
        return self.fc(x)


# Load pretrained weights using torchvision MNIST training
transform = transforms.Compose([transforms.ToTensor()])

trainset = torchvision.datasets.MNIST(
    root="./data", train=True, download=True, transform=transform
)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

model = Net()

# Quick training (only few batches for demo)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for i, (images, labels) in enumerate(trainloader):
    optimizer.zero_grad()
    outputs = model(images)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()

    if i > 100:  # short training for demo
        break

print("Training complete")

# Export to ONNX
dummy_input = torch.randn(1, 1, 28, 28)
torch.onnx.export(
    model,
    dummy_input,
    "mnist.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=11
)

print("mnist.onnx exported successfully")
