import util
from properties import *
from model import *
from trainerThu import TrainerThu
from trainerFb import TrainerFb
from evaluator import Evaluator
from myembedding import WordEmbeddings

import argparse
import copy
import os
import numpy as np

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser for Unsupervised Bilingual Lexicon Induction using GANs')
    parser.add_argument("--data_dir", dest="data_dir", type=str, default=DATA_DIR)
    parser.add_argument("--src_file", dest="src_file", type=str, default=EN_WORD_TO_VEC)
    parser.add_argument("--tgt_file", dest="tgt_file", type=str, default=IT_WORD_TO_VEC)
    parser.add_argument("--validation_file", dest="validation_file", type=str, default=VALIDATION_FILE)

    parser.add_argument("--g_input_size", dest="g_input_size", type=int, default=g_input_size)
    parser.add_argument("--g_output_size", dest="g_output_size", type=int, default=g_output_size)
    parser.add_argument("--d_input_size", dest="d_input_size", type=int, default=d_input_size)
    parser.add_argument("--d_hidden_size", dest="d_hidden_size", type=int, default=d_hidden_size)
    parser.add_argument("--d_output_size", dest="d_output_size", type=int, default=d_output_size)
    parser.add_argument("--mini_batch_size", dest="mini_batch_size", type=int, default=mini_batch_size)
    parser.add_argument("--gen_activation", dest="gen_activation", type=str, default=gen_activation)
    parser.add_argument("--dis_activation", dest="dis_activation", type=str, default=dis_activation)
    parser.add_argument("--dis_hidden_dropout", dest="dis_hidden_dropout", type=float, default=dis_hidden_dropout)
    parser.add_argument("--dis_input_dropout", dest="dis_input_dropout", type=float, default=dis_input_dropout)


    parser.add_argument("--d_learning_rate", dest="d_learning_rate", type=float, default=d_learning_rate)
    parser.add_argument("--g_learning_rate", dest="g_learning_rate", type=float, default=g_learning_rate)
    parser.add_argument("--num_epochs", dest="num_epochs", type=int, default=num_epochs)
    parser.add_argument("--d_steps", dest="d_steps", type=int, default=d_steps)
    parser.add_argument("--g_steps", dest="g_steps", type=int, default=g_steps)
    parser.add_argument("--smoothing", dest="smoothing", type=float, default=smoothing)
    parser.add_argument("--recon_weight", dest="recon_weight", type=float, default=recon_weight)
    parser.add_argument("--beta", dest="beta", type=float, default=beta)
    parser.add_argument("--clip_value", dest="clip_value", type=float, default=clip_value)
    parser.add_argument("--num_random_seeds", dest="num_random_seeds", type=int, default=num_random_seeds)

    parser.add_argument("--iters_in_epoch", dest="iters_in_epoch", type=int, default=iters_in_epoch)
    parser.add_argument("--most_frequent_sampling_size", dest="most_frequent_sampling_size", type=int, default=most_frequent_sampling_size)
    parser.add_argument("--print_every", dest="print_every", type=int, default=print_every)
    parser.add_argument("--lr_decay", dest="lr_decay", type=float, default=lr_decay)
    parser.add_argument("--lr_shrink", dest="lr_shrink", type=float, default=lr_shrink)
    parser.add_argument("--lr_min", dest="lr_min", type=float, default=lr_min)
    parser.add_argument("--add_noise", dest="add_noise", type=int, default=add_noise)
    parser.add_argument("--center_embeddings", dest="center_embeddings", type=int, default=center_embeddings)

    parser.add_argument("--noise_mean", dest="noise_mean", type=float, default=noise_mean)
    parser.add_argument("--noise_var", dest="noise_var", type=float, default=noise_var)

    parser.add_argument("--K", dest="K", type=int, default=K)
    parser.add_argument("--top_frequent_words", dest="top_frequent_words", type=int, default=top_frequent_words)

    parser.add_argument("--csls_k", dest="csls_k", type=int, default=csls_k)

    parser.add_argument("--mode", dest="mode", type=int, default=mode)
    parser.add_argument("--model_dir", dest="model_dir", type=str, default=MODEL_DIR)
    parser.add_argument("--model_file_name", dest="model_file_name", type=str, default="generator_weights_best_0.t7")

    parser.add_argument("--refine_top", dest="refine_top", type=int, default=refine_top)
    parser.add_argument("--cosine_top", dest="cosine_top", type=int, default=cosine_top)
    parser.add_argument("--mask_procrustes", dest="mask_procrustes", type=int, default=0)
    parser.add_argument("--num_refine", dest="num_refine", type=int, default=1)
    return parser.parse_args()


def _get_eval_params(params):
    params = copy.deepcopy(params)
    params.ks = [1, 5, 10]
    params.methods = ['nn', 'csls']
    params.models = ['procrustes', 'adv']
    params.refine = ['without-ref', 'with-ref']
    return params


def main():
    params = parse_arguments()

    if params.mode == 0:
        u = util.Utils(params)
        u.run()

    else:
        print("Reading embedding numpy files...")
        use_cuda = False
        if params.mode in [1,2]:
            use_cuda = True
        src_emb_array, tgt_emb_array = util.load_npy_two(params.data_dir, 'src.npy', 'tgt.npy')
        print("Done.")
        print("Converting arrays to embedding layers...")
        src_emb = util.convert_to_embeddings(src_emb_array, use_cuda)
        tgt_emb = util.convert_to_embeddings(tgt_emb_array, use_cuda)
        print("Done.")
        
        #src_emb.weight.data /= src_emb.weight.data.norm(2, dim=1).view((-1, 1))
        #tgt_emb.weight.data /= tgt_emb.weight.data.norm(2, dim=1).view((-1, 1))

        if params.center_embeddings > 0:
            util.center_embeddings(src_emb.weight.data)
            util.center_embeddings(tgt_emb.weight.data)


        if params.mode == 1:            # GAN   tune
            t = TrainerThu(params)
            g = t.train(src_emb, tgt_emb)

        if params.mode == 2:            # GAN   tune
            t = TrainerFb(params)
            g = t.train(src_emb, tgt_emb)

        elif params.mode == 7:
            we1 = WordEmbeddings()
            we1.load_from_word2vec_new('/data/data/' + 'wiki.en.vec')
            we2 = WordEmbeddings()
            we2.load_from_word2vec_new('/data/data/' + 'wiki.zh.vec')
            if params.center_embeddings > 0:
                    we1.center_embeddings()
                    we2.center_embeddings()

        else:
            raise "Invalid flag!"


if __name__ == '__main__':
    main()
