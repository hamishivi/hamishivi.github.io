---
layout: post
title: Results Replicating L1 for Tulu
tags: blog technical
description: Results replicating the recent L1 paper.
---

### Intro

> Note to reader: This blog post is a (lightly) edited version of a post I originally wrote in May 2025, but dropped due to getting busy with life. I've finally cleaned it up and shared it, but understand it's a bit out of date! Lots of interesting and cool work on LM overthinking and length control has come out since then, one example being [GDPO](https://arxiv.org/abs/2601.05242).

A large flaw of autoregressive thinking models is that their inference can simply go on and on. For example, if we take DeepSeek-R1 and provide it with a slightly nonsense riddle, it very quickly degrades into endless guess-and-checking:

<blockquote class="twitter-tweet" data-dnt="true" align="center"><p lang="en" dir="ltr">I asked the new R1 to &quot;Perform some calculation to estimate pi/7&quot; and I don&#39;t know if it&#39;s ever going to stop thinking</p>&mdash; Nathan Lambert (@natolambert) <a href="https://twitter.com/natolambert/status/1927870355084841256?ref_src=twsrc%5Etfw">May 28, 2025</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

This is partly just due to the fact that long CoTs take some time to generate, and can also be part of an issue known as *overthinking*, wherein models often think for longer and produce longer CoTs for problems they will eventually get wrong or they did not need to spend all that time on. There is a decent amount of literature on this at this point, and papers that propose to solve the issue by better learning how to allocate compute for questions.

One particular approach to solving this I found interesting earlier in the year was *L1: Controlling How Long A Reasoning Model Thinks With Reinforcement Learning*. The idea behind the paper is simple: let's just *reward the model for getting the length right* during RL training! (Perhaps) surprisingly, a fairly simple reward works well here. Doing everything during RL training is something I'm interested in doing right now, so I quite liked this, and worked a little on replicating this in [Open-Instruct](https://github.com/allenai/open_instruct), a post-training codebase I contribute to quite a bit.

In order to replicate, I set up a small setting I cared about: Given a math dataset, can I RL-train with an additional length control reward to achieve a 'reasonable' degree of length control without sacrificing quality? In particular, I was interested in the following properties:

- How sensitive is the setup to the precise reward?
- Do we get out-of-domain length generalisation? If I train on lengths 0-4096, will the model generate 8000 tokens if I ask?
- Do I observe inference-time scaling effects as I ask for longer and longer generations?
- If I train on just math, how well does length control generalise out?

Some of these questions are answered in the original paper in more detail, but I wanted to try getting my own answers!

### Setup

Let's get a bit more specific about the setup. For my experiments, I used a `Qwen-2.5-7B` model finetuned on the `Tulu 3 SFT` dataset for 2 epochs (following the same hyperparameters as the original Tulu 3 SFT, but with a max context length of 32768). This is the starting point for my experiments unless otherwise stated. Note that this model is **not** a thinking model out-of-the-box, so it doesn't really do long-CoT generations initially.

For data, I used the [Eurus 2 data](https://huggingface.co/datasets/PRIME-RL/Eurus-2-RL-Data), a large-ish collection of math and code data. I filtered out the code data.

Finally, I did all my training with GRPO. I think this *should* work with other online RL algorithms (e.g. PPO), but I used GRPO since it was straightforward. To be exact, I used the `grpo_fast` implementation in Open-Instruct, which includes some minor extra features like packing. Here's an example of a command I used to train:
```bash
dataset=ai2-adapt-dev/eurus2_ground_truth_with_random_max_length
python mason.py \
    --cluster ai2/augusta-google-1 \
    --pure_docker_mode \
    --image hamishivi/open_instruct_mult_dev1704 \
    --workspace ai2/tulu-3-dev \
    --priority high \
    --preemptible \
    --num_nodes 3 \
    --max_retries 0 \
    --budget ai2/oe-adapt \
    --gpus 8 -- source configs/beaker_configs/ray_node_setup.sh \&\& python open_instruct/grpo_fast.py \
    --exp_name $exp_name \
    --beta $beta \
    --num_samples_per_prompt_rollout 16 \
    --num_unique_prompts_rollout 128 \
    --sft_messages_key messages \
    --output_dir /output \
    --kl_estimator kl3 \
    --learning_rate 1e-6 \
    --dataset_mixer_list $dataset 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list $dataset 16 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 10240 \
    --max_prompt_token_length 1024 \
    --response_length 8192 \
    --model_name_or_path ai2-adapt-dev/tulu_3_long_finetune_qwen_7b_reg \
    --apply_verifiable_reward True \
    --non_stop_penalty False \
    --temperature 0.6 \
    --total_episodes 2000000 \
    --non_stop_penalty_value 0.0 \
    --pack_length 16384 \
    --deepspeed_stage 2 \
    --per_device_train_batch_size 1 \
    --num_learners_per_node 8 8 \
    --num_epochs 1 \
    --num_mini_batches 1 \
    --vllm_tensor_parallel_size 1 \
    --vllm_num_engines 8 \
    --lr_scheduler_type constant \
    --seed 1 \
    --num_evals 100 \
    --save_freq 2000 \
    --try_launch_beaker_eval_jobs_on_weka False \
    --gradient_checkpointing \
    --with_tracking
```

There are some minor changes for different datasets (with different length rewards), but really this is the main command and hyperparameters used.

What does our reward look like? I experimented with four different setups:

1. *"Exact" reward (4k)*: For each prompt, I sample randomly a length in range (100, 4096). I add to the prompt `\nThink for n tokens.` We then calculate the reward as `1 - (abs(tokenized_prediction - desired_length) / 8192)`, and add this to the ground truth reward (so the model gets extra reward for getting the length correct).
2. *"Exact" reward (8k)*: Same as above, but I randomly sample a length in range (100, 8192).
3. *"Exact" reward (bucketed)*: Same as above, but I only sample lengths from `{100, 1024, 2048, 4096, 6144, 8192}`. The idea is that learning specific 'valid' lengths might be easier than any integer in a range with > 4000 values.
4. *"Up to" reward (8k)*: We reward the model just for being under the token budget. Uses the same calculation as *1*, but if `tokenized_prediction - desired_length < 0`, we just give full reward. The idea is that this is an easier task to learn, and a bit more realistic (a user probably doesn't mind if the model finishes early). Note that I edit the prompt to be `\nThink for up to n tokens.`

To visualise the "up to" and "exact" rewards for a desired length of 3200 tokens:
<img src="https://i.imgur.com/1Z5NGlO.png" alt="Reward visualisation" width="500" style="display: block; margin: 0 auto;">

How do we evaluate? Basically, I evaluated on MATH-500 with desired lengths of `{100, 1024, 2048, 4096, 6144, 8192, 9216, 10240}` (set via the prompt). I measure both performance at the various lengths and how far off the lengths are from the desired output length (shown via violin plot below). I also did one out-of-domain experiment running evaluation on MMLU with the same lengths.

### Results

#### How well do the different approaches adhere to length budget?

Let's start by just looking at how well each approach actually adheres to the length budget. We use a violin plot to show the distribution of lengths generated by the model for each desired length, and remove the bottom and top 5% of lengths to reduce the effect of outliers.

1. **"Exact" reward (4k)**: This works well but we see the model doesn't generalise to lengths past ~4000, even though it was allowed to generate up to 8k during training. This suggests that this form of length control *doesn't generalise to new lengths*.

<img src="https://i.imgur.com/r2dhxk1.png" alt="Exact reward (4k)" width="500" style="display: block; margin: 0 auto;">

2. **"Exact" reward (8k)**: This also works well! But again, past 8000 desired length it falls apart. I found that upping the learning rate and training for longer generally improved the model's adherence to the length budget.

<img src="https://i.imgur.com/wqkCPhS.png" alt="Exact reward (8k)" width="500" style="display: block; margin: 0 auto;">

3. **"Exact" reward (bucketed)**: The model does very well at adhering to the bucketed values it was trained on, and again doesn't generalise further.

<img src="https://i.imgur.com/yKAzTnh.png" alt="Exact reward (bucketed)" width="500" style="display: block; margin: 0 auto;">

4. **"Up to" reward (8k)**: This seems to just encourage the model to always be short (although it does still stay in budget, technically!).

<img src="https://i.imgur.com/XMnRMUz.png" alt="Up to reward (8k)" width="500" style="display: block; margin: 0 auto;">

**Takeaways**: Training on the budget works really well! We get pretty good length control, although it's not exact exact. However, we don't generalise to new lengths, and so we can't use this technique to scale inference-time compute beyond what we used during training. Interestingly, we also see an 'up to' reward doesn't work that well, as the model just learns to always be short: instead, we need the tight 'exact' reward.

#### What about performance?

You might be curious about performance. Below I've plotted performance at different output lengths for the 8k "exact" reward (and I found the other methods to be similar in performance, apart from the 'up to' reward which just learns to be short).

<img src="https://i.imgur.com/GEWJ4Z7.png" alt="Performance at different lengths" width="500" style="display: block; margin: 0 auto;">

As you can see, the model matches the performance of the 'no length control' baseline once we hit >= 2000 tokens in output. This suggests: **a:** we can get length control without sacrificing performance, and **b:** the model doesn't need to generate long chains to do well. **b** is especially interesting, since the model without length control is fairly yappy and does make use of the full 8k token budget quite often. This suggests that the model **learns to compress its reasoning as part of the length control task**. Perhaps this would drop performance in more complex tasks, but here it's very encouraging. Indeed, much work over the past year found that reasoning models could compress their reasoning chains quite a lot.

#### What about out-of-domain generalisation?

Finally, I also wanted to see how well the length control did at tasks that were OOD. Recall we are training on math data only, so I evaluated on MMLU, which is a general QA task.

<img src="https://i.imgur.com/isTJDob.png" alt="Length control on MMLU" width="500" style="display: block; margin: 0 auto;">

Here, we see that **length control still works, but less strongly** on these OOD tasks. I consider this pretty successful, since in reality we can just train on a diverse mixture and minimise how many OOD cases the model needs to deal with (and later for Olmo 3 we did indeed train on a moderately diverse mixture of data).

Sadly, we do see performance drop:

<img src="https://i.imgur.com/AynOhoN.png" alt="MMLU performance comparison" width="500" style="display: block; margin: 0 auto;">

Note that 'bucketed' is the bucketed reward mentioned above, and the other two are the 'exact' rewards trained for differing amounts of time with different LRs. All three perform worse than the base model. However, this might just be due to the model overfitting on the training data (math-only), for which I don't have an experiment.

### Conclusion

I did this project to answer a few questions, and we can now clearly do that:

- *How sensitive is the setup to the precise reward?*
    - It seems that the model is not thaaaat sensitive to the setup (naive summing works, bucketing works), but we do need the 'exact' reward to avoid the model always being short. Later work such as [GDPO](https://arxiv.org/abs/2601.05242) has improved length control adherence with tweaks to the RL algorithm. 
- *Do we get out-of-domain length generalisation? If I train on lengths 0-4096, will the model generate 8000 tokens if I ask?*
    - Sadly, no! This really sucks, and is partly why I moved on from these results. It would be interesting to see if more work on the setup could change this (meta-learning? mixing in unfinished samples?)
- *Do I observe inference-time scaling effects as I ask for longer and longer generations?*
    - Yes, weakly so! Our data and eval were 'too easy' such that past 2k tokens the model could just do really well, but we still see some inference-time scaling effects.
- *If I train on just math, how well does length control generalise out?*
    - Surprisingly well! It's not as good as training on a diverse mixture, but it's still pretty good. This suggests that the model is learning to generalise length control to new tasks, and that the length control task is not too difficult.

Overall, I think these show that an L1-style recipe is pretty effective at learning token budgets. If you use coarse buckets (e.g. 'easy', 'medium', 'hard' reasoning), you can do really well, and even exact token budgets are possible with training, and don't seem to sacrifice performance too much. Revisiting these results has reminded me to try to fold these into the next Olmo release, which I will (try) to do.

Thanks for reading, and may your LMs be perfectly verbose.