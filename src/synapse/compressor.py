import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any

class Compressor:
    def __init__(self, model_name: str = "distilgpt2", device: str = None):
        self.model_name = model_name
        self.device = device or ("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = None
        self.tokenizer = None

    def _load_model(self):
        if self.model is None:
            # print(f"Loading compression model: {self.model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            self.model.eval()

    def get_token_loss(self, text: str) -> torch.Tensor:
        """
        Calculate the loss for each token in the text.
        Handles long texts by chunking.
        """
        self._load_model()
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        input_ids = inputs.input_ids[0] # Shape: [seq_len]
        
        # Model context size (distilgpt2 = 1024)
        max_len = getattr(self.model.config, "n_positions", 1024)
        
        all_losses = []
        
        for i in range(0, len(input_ids), max_len):
            chunk_ids = input_ids[i : i + max_len].unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(chunk_ids, labels=chunk_ids)
                shift_logits = outputs.logits[..., :-1, :].contiguous()
                shift_labels = chunk_ids[..., 1:].contiguous()
                
                loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
                
                # Prepend a 0 for the first token to match length
                loss = torch.cat([torch.tensor([0.0]).to(self.device), loss])
                
                all_losses.append(loss)
        
        full_loss = torch.cat(all_losses)
        return full_loss, input_ids

    def compress(self, context: str, rate: float = 0.5, instruction: str = "", question: str = "") -> str:
        """
        Compress the context by keeping tokens with high perplexity (surprise).
        Simple implementation of LLMLingua core logic.
        """
        if not context or rate >= 1.0:
            return context

        self._load_model()
        
        # Combine instruction, question, and context for full context PPL, 
        # but we only compress the 'context' part usually.
        # For simplicity in this CLI tool, we treat the input 'context' as the text to compress.
        # If instruction/question provided, we prepend/append but focus on compressing the middle.
        
        full_text = f"{instruction}\n{context}\n{question}".strip()
        loss, input_ids = self.get_token_loss(full_text)
        
        # We need to map loss back to the context tokens.
        # input_ids has length N. loss has length N-1.
        # loss[i] corresponds to prediction of input_ids[i+1] given input_ids[:i+1]
        
        # Strategy:
        # 1. Calculate threshold based on rate.
        # 2. Keep tokens where loss > threshold.
        # 3. Always keep special tokens or formatting if possible (heuristic).
        
        # Calculate target count
        n_tokens = len(loss)
        target_count = int(n_tokens * rate)
        
        if target_count == 0:
            return ""

        # Find threshold
        # We want top 'rate' percent of tokens (highest loss)
        # sort descending
        sorted_loss, _ = torch.sort(loss, descending=True)
        threshold = sorted_loss[target_count]
        
        # Generate mask
        # We keep token if loss >= threshold
        keep_mask = loss >= threshold
        keep_mask[0] = True # Always keep start of document

        # Heuristics: Always keep newlines to preserve code structure
        # Identify tokens containing newline
        unique_ids = torch.unique(input_ids)
        newline_ids = []
        for uid in unique_ids:
            # Decode single token
            tok = self.tokenizer.decode([uid])
            if "\n" in tok:
                newline_ids.append(uid.item())
        
        # Force keep newline tokens
        if newline_ids:
            newline_tensor = torch.tensor(newline_ids).to(self.device)
            is_newline = torch.isin(input_ids, newline_tensor)
            keep_mask = keep_mask | is_newline

        # Heuristics: Force keep 'def' and 'class' keywords to preserve structure
        # Identify tokens containing these keywords
        keyword_ids = []
        target_keywords = ["def", "class", "return", "import", "from"]
        for uid in unique_ids:
            tok = self.tokenizer.decode([uid]).strip()
            if tok in target_keywords:
                keyword_ids.append(uid.item())
        
        if keyword_ids:
            kw_tensor = torch.tensor(keyword_ids).to(self.device)
            is_kw = torch.isin(input_ids, kw_tensor)
            keep_mask = keep_mask | is_kw

        # Heuristics: Keep function/class names (token after def/class)
        def_class_keywords = ["def", "class"]
        def_class_ids = []
        for uid in unique_ids:
            tok = self.tokenizer.decode([uid]).strip()
            if tok in def_class_keywords:
                def_class_ids.append(uid.item())
        
        if def_class_ids:
             dc_tensor = torch.tensor(def_class_ids).to(self.device)
             is_dc = torch.isin(input_ids, dc_tensor)
             # Get indices
             dc_indices = torch.nonzero(is_dc).squeeze()
             if dc_indices.numel() > 0:
                 if dc_indices.dim() == 0:
                     dc_indices = dc_indices.unsqueeze(0)
                 
                 next_indices = dc_indices + 1
                 # Filter out of bounds
                 next_indices = next_indices[next_indices < len(input_ids)]
                 keep_mask[next_indices] = True

        compressed_ids = input_ids[keep_mask]
        compressed_text = self.tokenizer.decode(compressed_ids, skip_special_tokens=True)
        
        return compressed_text

    def compress_documents(self, documents: List[str], rate: float = 0.5) -> List[str]:
        return [self.compress(doc, rate) for doc in documents]
