from config.config import POLICY_CONFIG, TASK_CONFIG, TRAIN_CONFIG # must import first

import os
import pickle
import argparse
from copy import deepcopy
import matplotlib.pyplot as plt

from training.utils import *

# parse the task name via command line
parser = argparse.ArgumentParser()
parser.add_argument('--task', type=str, default='task1')
args = parser.parse_args()
task = args.task

# configs
task_cfg = TASK_CONFIG
train_cfg = TRAIN_CONFIG
policy_config = POLICY_CONFIG
checkpoint_dir = os.path.join(train_cfg['checkpoint_dir'], task)

# device
device = os.environ['DEVICE']


def forward_pass(data, policy):
    image_data, qpos_data, action_data, is_pad = data
    image_data, qpos_data, action_data, is_pad = image_data.to(device), qpos_data.to(device), action_data.to(device), is_pad.to(device)
    return policy(qpos_data, image_data, action_data, is_pad) # TODO remove None

def forward_pass_extra(data, policy):
    image_data, qpos_data, action_data, is_pad = data
    image_data, qpos_data, action_data, is_pad = image_data.to(device), qpos_data.to(device), action_data.to(device), is_pad.to(device)
    
    # Perform the forward pass
    output = policy(qpos_data, image_data, action_data, is_pad)
    
    # Return both inputs and outputs
    return {'inputs': (image_data, qpos_data, action_data, is_pad), 'outputs': output}

def plot_history(train_history, validation_history, num_epochs, ckpt_dir, seed):
    # save training curves
    for key in train_history[0]:
        plot_path = os.path.join(ckpt_dir, f'train_val_{key}_seed_{seed}.png')
        plt.figure()
        train_values = [summary[key].item() for summary in train_history]
        val_values = [summary[key].item() for summary in validation_history]
        plt.plot(np.linspace(0, num_epochs-1, len(train_history)), train_values, label='train')
        plt.plot(np.linspace(0, num_epochs-1, len(validation_history)), val_values, label='validation')
        # plt.ylim([-0.1, 1])
        plt.tight_layout()
        plt.legend()
        plt.title(key)
        plt.savefig(plot_path)
    print(f'Saved plots to {ckpt_dir}')


def train_bc(train_dataloader, val_dataloader, policy_config):
    # load policy
    policy = make_policy(policy_config['policy_class'], policy_config)
    policy.to(device)

    # load optimizer
    optimizer = make_optimizer(policy_config['policy_class'], policy)

    # create checkpoint dir if not exists
    os.makedirs(checkpoint_dir, exist_ok=True)

    train_history = []
    validation_history = []
    min_val_loss = np.inf
    best_ckpt_info = None
    for epoch in range(train_cfg['num_epochs']):
        print(f'\nEpoch {epoch}')
        # validation
        with torch.inference_mode():
            policy.eval()
            epoch_dicts = []
            for batch_idx, data in enumerate(val_dataloader):
                forward_dict = forward_pass(data, policy)
                epoch_dicts.append(forward_dict)
            epoch_summary = compute_dict_mean(epoch_dicts)
            validation_history.append(epoch_summary)

            epoch_val_loss = epoch_summary['loss']
            if epoch_val_loss < min_val_loss:
                min_val_loss = epoch_val_loss
                best_ckpt_info = (epoch, min_val_loss, deepcopy(policy.state_dict()))
        print(f'Val loss:   {epoch_val_loss:.5f}')
        summary_string = ''
        for k, v in epoch_summary.items():
            summary_string += f'{k}: {v.item():.3f} '
        print(summary_string)

        # training
        policy.train()
        optimizer.zero_grad()

        for batch_idx, data in enumerate(train_dataloader):
            print('batch_idx: ', batch_idx)
            forward_dict = forward_pass(data, policy)
            import pdb;pdb.set_trace()
            result = forward_pass_extra(data, policy)
            inputs, outputs = result['inputs'], result['outputs']
    

            # Print inputs and outputs
            print(f"Batch {batch_idx}:")
            print("Inputs:")
            # print("Image Data:", inputs[0])
            print("Qpos Data:", inputs[1])
            print("Action Data (Ground Truth):", inputs[2])
            # print("Is Padding:", inputs[3])
            print("Outputs:", outputs)
            import pdb;pdb.set_trace()

            
            
            '''(Pdb) forward_dict
{'l1': tensor(2.5544, grad_fn=<MeanBackward0>), 'kl': tensor(11.8251, grad_fn=<SelectBackward0>), 'loss': tensor(120.8051, grad_fn=<AddBackward0>)}
            '''
            # backward
            loss = forward_dict['loss']
            # TODO 
            '''
            /home/ben/all_projects/imitation_learning_fun/training/policy.py:32: 
            UserWarning: Using a target size (torch.Size([2, 100, 5])) 
            that is different to the input size (torch.Size([2, 100, 1])). This will likely lead to incorrect results due to broadcasting. Please ensure they have the same size.
            all_l1 = F.l1_loss(actions, a_hat, reduction='none')
            '''
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            train_history.append(detach_dict(forward_dict))

        epoch_summary = compute_dict_mean(train_history[(batch_idx+1)*epoch:(batch_idx+1)*(epoch+1)])
        epoch_train_loss = epoch_summary['loss']
        print(f'Train loss: {epoch_train_loss:.5f}')
        summary_string = ''
        for k, v in epoch_summary.items():
            summary_string += f'{k}: {v.item():.3f} '
        print(summary_string)

        if epoch % 2 == 0:
            plot_history(train_history, validation_history, epoch, checkpoint_dir, train_cfg['seed'])
            if epoch % 10 == 0:
                ckpt_path = os.path.join(checkpoint_dir, f"policy_epoch_{epoch}_seed_{train_cfg['seed']}.ckpt")
                torch.save(policy.state_dict(), ckpt_path)

    ckpt_path = os.path.join(checkpoint_dir, f'policy_last.ckpt')
    torch.save(policy.state_dict(), ckpt_path)
    

if __name__ == '__main__':
    # set seed
    set_seed(train_cfg['seed'])
    # create ckpt dir if not exists
    os.makedirs(checkpoint_dir, exist_ok=True)
    # number of training episodes
    data_dir = os.path.join(task_cfg['dataset_dir'], task)
    num_episodes = len(os.listdir(data_dir))

    # load data
    train_dataloader, val_dataloader, stats, _ = load_data(data_dir, num_episodes, task_cfg['camera_names'],
                                                            train_cfg['batch_size_train'], train_cfg['batch_size_val'])
    # save stats
    stats_path = os.path.join(checkpoint_dir, f'dataset_stats.pkl')
    with open(stats_path, 'wb') as f:
        pickle.dump(stats, f)

    # train
    train_bc(train_dataloader, val_dataloader, policy_config)