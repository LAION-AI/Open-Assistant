import argparse
from tranformers import 



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--model_name", type=str, help="Model url or filepath")
    parser.add_argument("--max_length", type=str, help="Maximum sequence length for the model")
    parser.add_argument("--stride", type=str, help="Stride for data chunks")
    parser.add_argument("--bit", type=str, help="Model url or filepath") ## [4,8,16,32]
    parser.add_argument("--is_lora", type=bool, help="")
    
    #TODO
    # Load model 
    # Load dataset
    # Prepare dataset
    # Measure perplexity 
    # plot results
    # save results
    
    
    

