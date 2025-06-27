import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pix2text_model = ORTModelForVision2Seq.from_pretrained("./pix2text-mfr", use_cache=False)
processor = TrOCRProcessor.from_pretrained("./pix2text-mfr")

nemeth_model_path = "latex_to_nemeth_model_final"
nemeth_model = AutoModelForSeq2SeqLM.from_pretrained(nemeth_model_path, local_files_only=True).to(device)
nemeth_tokenizer = AutoTokenizer.from_pretrained(nemeth_model_path, local_files_only=True)
