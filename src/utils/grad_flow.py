### Source: https://github.com/alwynmathew/gradflow-check/blob/master/gradflow_check.py

import matplotlib.pyplot as plt

from matplotlib.lines import Line2D

import numpy as np
import torch

import io

import PIL.Image

plt.ioff() ## Interactive mode is off

def figure_to_array(figure):
    
    buf = io.BytesIO()
    plt.savefig(figure, format = 'png')
    buf.seek(0)
    
    array = Image.open(buf)
    return array


def plot_grad_flow_v2(named_parameters):
    '''Plots the gradients flowing through different layers in the net during training.
    Can be used for checking for possible gradient vanishing / exploding problems.
    
    Usage: Plug this function in Trainer class after loss.backwards() as 
    "plot_grad_flow(self.model.named_parameters())" to visualize the gradient flow'''
    ave_grads = []
    max_grads= []
    layers = []
    
    plt.figure(figsize = (20, 8))
    
    with torch.no_grad():
        for n, p in named_parameters:
            if(p.requires_grad) and ("bias" not in n):
                
                try:
                    layers.append(n)            
                    ave_grads.append(p.grad.abs().mean().cpu()) ## Transfer grad tensor to CPU
                    max_grads.append(p.grad.abs().max().cpu())  ## Transfer grad tensor to CPU
                except:
                    print(f"parameter shape is: {p.shape}, parameter name is: {n}")
                    
        plt.bar(np.arange(len(max_grads)), max_grads, alpha=0.1, lw=1, color="c")
        plt.bar(np.arange(len(max_grads)), ave_grads, alpha=0.1, lw=1, color="b")
        plt.hlines(0, 0, len(ave_grads)+1, lw=2, color="k" )
        plt.xticks(range(0,len(ave_grads), 1), layers, rotation="vertical")
        plt.xlim(left=0, right=len(ave_grads))
        plt.ylim(bottom = -0.001, top=0.02) # zoom in on the lower gradient regions
        plt.xlabel("Layers")
        plt.ylabel("average gradient")
        plt.title("Gradient flow")
        plt.grid(True)
        plt.legend([Line2D([0], [0], color="c", lw=4),
                    Line2D([0], [0], color="b", lw=4),
                    Line2D([0], [0], color="k", lw=4)], ['max-gradient', 'mean-gradient', 'zero-gradient'])

        figure = plt.gcf() ## Get the current figure
    
    plt.close() ## Clear the current window
        
    return figure
