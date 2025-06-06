# Download Models Locally
## Download Llama Models

### Step 1: Download the Llama Model
Download the **LLaMA 3.3B Instruct** model from [Llama's official website](https://www.llama.com/llama-downloads/) and follow the installation instructions.

### Step 2: Set Up the Models Directory
Once the model is installed successfully on your machine:

1. Create a `models` directory in your project folder.
2. Move the `~/.llama` directory into the `models` folder.

### Step 3: Clone the Llama Models Repository
Please run:

```sh
cd models
git clone https://github.com/meta-llama/llama-models
```

### Step 4: Copy Python Scripts
After cloning the repository, copy all `.py` files to the appropriate scripts directory:

```sh
cp scripts/llama/*.py models/llama-models/llama_models/scripts/
```

## Download PhoGPT Models
Download the **PhoGPT-4B** model by cloning it into the `models` directory:

```sh
cd models
git clone https://huggingface.co/vinai/PhoGPT-4B
```

---

# Running the Models

- **For GPT-4, PhoGPT, URA-LLaMA**: Navigate to `scripts/[model_name]` and run:
  ```sh
  python [jailbreaking_method].py
  ```
- **For LLaMA**: Navigate to `scripts/llama` and run:
  ```sh
  sh [jailbreaking_method].sh
  ```

## Important Notes
- **GPT-4**: Please use your OpenAI key.
- **URA-LLaMA**: Contact us to obtain the required key.


