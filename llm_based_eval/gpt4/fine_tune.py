import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_ID = "Upstage/SOLAR-10.7B-Instruct-v1.0"

tokenizer = AutoTokenizer.from_pretrained(model_ID)
model = AutoModelForCausalLM.from_pretrained(
	model_ID,
	device_map="auto",
	torch_dtype=torch.float16,
)

optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)
loss_function = torch.nn.CrossEntropyLoss()

num_epochs = 20

for epoch in range(num_epochs):
    for step, batch in enumerate(train_dataloader):
        inputs, labels = batch
        outputs = model(inputs)
        loss = loss_function(outputs, labels)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

