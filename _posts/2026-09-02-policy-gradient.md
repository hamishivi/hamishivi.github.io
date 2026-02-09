---
layout: post
title: "Introduction to Policy Gradient for LMs"
tags: blog technical rl nlp
mathjax: true
description: A basic introduction to policy gradient for language models.
---

These are a lightly adapted set of notes for a 'RL101' lecture I gave for some research groups meetings. These aim to be a reasonably thorough introduction to policy gradient, specifically in the context of language models. I go far enough to get to CISPO (which honestly is pretty much one of the better algorithms out there right now), but I don't cover all the way to PPO.
These notes are adapted from when I took RL here at UW.

## Terminology

We will use the standard Markov Decision Process (MDP) model

$$
\mathcal{M} = (\mathcal{S},\mathcal{A},P,r,\gamma,\rho_0).
$$

| **Term** | **MDP notation** | **LM analogue** | **LM notation** |
|----------|------------------|-----------------|-----------------|
| State | $s\in\mathcal{S}$ | prompt + prefix tokens | $s_t \equiv x_{0:t}$ |
| Action | $a\in\mathcal{A}$ | next token | $a_t \equiv x_{t+1}$ |
| Transition | $P(s'\mid s,a)$ | append token (usually deterministic) | $s_{t+1}=(s_t,a_t)$ |
| Reward | $r(s,a)$ | terminal score / reward model | $r_T$ (often at EOS) |
| Discount | $\gamma\in[0,1)$ | (optional) token-position discount | $\gamma$ |
| Start state dist. | $\rho_0$ | prompt distribution | $p(\text{prompt})$ |
| Policy | $\pi_\theta(a\mid s)$ | LM next-token distribution | $p_\theta(x_{t+1}\mid x_{0:t})$ |
| Trajectory | $\tau=(s_0,a_0,\dots,s_T)$ | completion / rollout | $\tau \equiv x_{0:T}$ |
| Return | $R(\tau)=\sum_{t=0}^{T-1}\gamma^t r(s_t,a_t)$ | scalar score for completion | $R(x_{0:T})$ |

**Policy / LM distribution.**
In general RL notation, our policy is a conditional distribution $\pi_\theta(a\mid s)$.
For an autoregressive language model, we will identify

$$
\pi_\theta(a_t\mid s_t) \equiv p_\theta(x_{t+1}\mid x_{0:t}).
$$

With this identification, the probability of a full completion (trajectory) factors as

$$
\pi_\theta(\tau) \equiv p_\theta(x_{0:T}) = p(x_0)\prod_{t=0}^{T-1} p_\theta(x_{t+1}\mid x_{0:t}),
$$

where $p(x_0)$ denotes the prompt distribution (or is treated as fixed/conditioned on).

Note that we call discounting optional because most LM RL work sets $\gamma = 1$ and only has a single reward at the end of the trajectory. However, sometimes we change this (e.g., in scenarios where dense reward is available).

## Deriving PG

In policy gradient, we assume a differentiable, parameterized policy $\pi_\theta$ and update parameters by (stochastic) gradient *ascent* on $J(\theta)$:

$$
\theta \leftarrow \theta + \alpha\,\widehat{\nabla_\theta J(\theta)}.
$$

An important initial identity is the log-deriv trick:

$$
\begin{aligned}
\nabla_\theta \log \pi_\theta(\tau)
&= \frac{\nabla_\theta \pi_\theta(\tau)}{\pi_\theta(\tau)}
\quad\text{(when $\pi_\theta(\tau)>0$)}\\[0.5em]
\nabla_\theta \pi_\theta(\tau)
&= \pi_\theta(\tau)\,\nabla_\theta \log \pi_\theta(\tau)
\end{aligned}
$$

We want to maximise our expected reward, that is we set:

$$
\begin{aligned}
J(\theta) &= \mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)] \\
&= \int \pi_\theta(\tau)\,R(\tau)\,d\tau
\end{aligned}
$$

Now, let's compute the derivative:

$$
\begin{aligned}
\nabla_\theta J(\theta)
&= \nabla_\theta \int \pi_\theta(\tau)\,R(\tau)\,d\tau \\
&= \int \nabla_\theta\pi_\theta(\tau)\,R(\tau)\,d\tau \\
&= \int \pi_\theta(\tau)\,\nabla_\theta\log\pi_\theta(\tau)\,R(\tau)\,d\tau
\end{aligned}
$$

Then, we expand out the trajectory logprobs. Finally, expand the trajectory log-probability:

$$
\begin{aligned}
\log\pi_\theta(\tau)
&= \log\rho_0(s_0) + \sum_{t=0}^{T-1}\log\pi_\theta(a_t\mid s_t) + \sum_{t=0}^{T-1}\log P(s_{t+1}\mid s_t,a_t) \\[0.5em]
\nabla_\theta\log\pi_\theta(\tau) &= \nabla_\theta\log\rho_0(s_0) + \nabla_\theta\sum_{t=0}^{T-1}\log\pi_\theta(a_t\mid s_t) + \nabla_\theta\sum_{t=0}^{T-1}\log P(s_{t+1}\mid s_t,a_t) \\
&= \sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta(a_t\mid s_t)
\end{aligned}
$$

Interestingly, the transition dynamics disappear completely! Although, of course, they still are affecting the trajectory distribution implicitly. So we can just plug that right in:

$$
\nabla_\theta J(\theta)
= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,R(\tau)\right]
$$

Next, we will define the "reward-to-go" (the future return from time $t$):

$$
G_t \triangleq \sum_{k=t}^{T-1} \gamma^{k-t}\,r(s_k,a_k)
$$

Importantly, we can note that the reward-to-go is the only thing that matters in our derivative.
Write the full return as a "past" part plus a "future" part:

$$
\begin{aligned}
R(\tau)
&= \sum_{k=0}^{T-1} \gamma^k r(s_k,a_k)\\
&= \underbrace{\sum_{k=0}^{t-1} \gamma^k r(s_k,a_k)}_{\triangleq\,R_{<t}} + \underbrace{\sum_{k=t}^{T-1} \gamma^k r(s_k,a_k)}_{\triangleq\,G_t}
\end{aligned}
$$

Then, for any fixed time $t$,

$$
\begin{aligned}
\mathbb{E}_{\tau\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,R(\tau)\big]
&= \mathbb{E}_{\tau\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t + R_{<t})\big]\\
&= \mathbb{E}_{\tau\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\big]
+ \underbrace{\mathbb{E}_{\tau\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,R_{<t}\big]}_{=0}
\end{aligned}
$$

The last term is zero because conditioning on $s_t$, $R_{<t}$ is a valid baseline. Let's put a pin in this for a second, and come back to it later.

This gives us our REINFORCE loss:

$$
\mathcal{L}_{\text{REINFORCE}}(\theta)
\;\triangleq\; -\,\mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \log\pi_\theta(a_t\mid s_t)\,G_t\right]
$$

And our basic algorithm:

1. Initialize policy parameters $\theta$.
2. Repeat for iterations $k=0,1,2,\dots$:
   1. Sample a batch of trajectories $\\{\tau^{(i)}\\}\_{i=1}^N$ by rolling out the current policy $\pi_\theta$.
   2. For each trajectory $\tau^{(i)}=(s_0^{(i)},a_0^{(i)},\dots,s_T^{(i)})$, compute the rewards $r(s_t^{(i)},a_t^{(i)})$ and reward-to-go values $G_t^{(i)}$ for all $t$.
   3. Form the Monte Carlo gradient estimate (using reward-to-go):
      $$
      \widehat{\nabla_\theta J(\theta)}
      = \frac{1}{N}\sum_{i=1}^N\sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta\big(a_t^{(i)}\mid s_t^{(i)}\big)\,G_t^{(i)}
      $$
   4. Update the parameters by gradient ascent:
      $$
      \theta \leftarrow \theta + \alpha\,\widehat{\nabla_\theta J(\theta)}
      $$

### Issues with REINFORCE

There are three core issues with REINFORCE:

1. **High Variance**: The reward values can vary a bunch, and even have weird scale. Consider a reward that's always negative. Basically, we want to normalize things a little.
2. **Unknown step size**: We don't really know the right learning rate to use, especially since this actually might change over training, unlike regular ML.
3. **Data reuse**: We can't reuse data from prior loops, since we have defined our loss and gradient over the current policy.

I'll cover two of these, and step size is... less of a big issue for things like CISPO, but is important and part of the motivation for developing things like TRPO and PPO.
Let's deal with variance first, since that's the most important thing.

### Baselining

A standard variance-reducing trick is to subtract a baseline that only relies on the current state:

$$
\nabla_\theta J(\theta)
= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t - b(s_t))\right]
$$

We need to show two core things: (1) that doing this is unbiased, and doesn't change our result; (2) that this actually reduces variance.

#### Unbiasedness

Let's split out our loss:

$$
\begin{aligned}
\nabla_\theta J(\theta)
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t - b(s_t))\right] \\
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right]
- \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,b(s_t)\right]
\end{aligned}
$$

Then, we will just consider the baseline term. Let's consider what happens at a single time step $t$. The key thing is we split up the expectation:

$$
\begin{aligned}
\mathbb{E}_{\tau\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,b(s_t)\big]
&= \mathbb{E}_{s_t,a_t\sim\pi_\theta}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,b(s_t)\big]\\
&= \mathbb{E}_{s_t}\left[\mathbb{E}_{a_t\sim\pi_\theta(\cdot\mid s_t)}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,b(s_t)\ \big|\ s_t\big]\right]\\
&= \mathbb{E}_{s_t}\left[b(s_t)\,\mathbb{E}_{a_t\sim\pi_\theta(\cdot\mid s_t)}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\big]\right]\\
&= \mathbb{E}_{s_t}\left[b(s_t)\,\sum_a \pi_\theta(a\mid s_t)\,\nabla_\theta\log\pi_\theta(a\mid s_t)\right]\\
&= \mathbb{E}_{s_t}\left[b(s_t)\,\sum_a \nabla_\theta\pi_\theta(a\mid s_t)\right]\\
&= \mathbb{E}_{s_t}\left[b(s_t)\,\nabla_\theta\sum_a \pi_\theta(a\mid s_t)\right]
= \mathbb{E}_{s_t}\left[b(s_t)\,\nabla_\theta 1\right]
= 0
\end{aligned}
$$

Therefore

$$
\mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,b(s_t)\right] = 0,
$$

so replacing $G_t$ by $G_t-b(s_t)$ leaves the expectation unchanged (i.e., the estimator remains unbiased).

Note that this is why up to the current state is okay: if the current action was included, then we couldn't move the baseline out of the expectation in the above proof. So we can depend on anything apart from the current action for our baseline.

#### Variance Reduction

Now we know we can do this, we need to consider what would be a good baseline that can reduce our variance?

The math for optimal baselines gets more involved, and I couldn't find a clear explanation, so let's stick with a higher-level approximation[^seita]. These approximations are not strictly valid in general, but they help us build some intuition for why we can reduce variance with baselines. Consider computing the variance of a single trajectory:

$$
\begin{aligned}
\mathrm{Var}\Big(\sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t-b(s_t))\Big)
&\approx^{(i)} \sum_{t=0}^{T-1}\mathbb{E}_{\tau}\Big[\big(\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t-b(s_t))\big)^2\Big]\\
&\approx^{(ii)} \sum_{t=0}^{T-1}\mathbb{E}_{\tau}\Big[\big(\nabla_\theta\log\pi_\theta(a_t\mid s_t)\big)^2\Big]\,\mathbb{E}_{\tau}\Big[\big(G_t-b(s_t)\big)^2\Big]
\end{aligned}
$$

Here (i) drops cross-covariance terms between different time steps, and (ii) further treats the score term and the (centered) return term as approximately independent. We can't control the variance over the logprobs, so instead we want to minimize just $G_t - b(s_t)$! This suggests that a good baseline is our best guess at $G_t$ based on $s_t$, **which is exactly our value function!**

This gives us the **advantage function**:

$$
A_{\pi_\theta}(s_t, a_t) = G_t - \hat{V}_{\pi_\theta}(s_t)
$$

Note here that $G_t$ is the reward we get from doing $a_t$ in state $s_t$. That is, it is (an unbiased Monte Carlo estimate of) the Q-value. Intuitively, we are replacing **weighting by absolute reward** with **weighting by the improvement of the action over the average action taken by the policy**. This intuitively reduces variance since we are sort of taking into account "how good" our policy is already.

### Re-using Old Data

Let's cover the other big issue with REINFORCE: data reuse.

We can't really re-use old data in our current setup, since we derived everything under the assumption that we drew our trajectories from our current model ($\tau \sim \pi_\theta$). This means that once we take a gradient step, the old trajectories are technically coming from a different distribution ($\tau \sim \pi_{\theta_{t-1}}$).

We can apply **importance weighting** to fix this. The core idea is that we can draw samples from a different distribution so long as we reweight the samples with the probabilities under our current distribution. To simplify, let's define

$$
\begin{aligned}
\mathbb{E}_{\tau\sim\pi_{\theta}}\big[f(\tau)\big]
&= \int \pi_{\theta}(\tau)\,f(\tau)\,d\tau \\
&= \int \pi_{\theta_{\mathrm{old}}}(\tau)\,\frac{\pi_{\theta}(\tau)}{\pi_{\theta_{\mathrm{old}}}(\tau)}\,f(\tau)\,d\tau \\
&= \mathbb{E}_{\tau\sim\pi_{\theta_{\mathrm{old}}}}\Big[w(\tau)\,f(\tau)\Big]
\end{aligned}
$$

where

$$
w(\tau) \triangleq \frac{\pi_{\theta}(\tau)}{\pi_{\theta_{\mathrm{old}}}(\tau)}
= \prod_{t=0}^{T-1}\frac{\pi_{\theta}(a_t\mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t\mid s_t)}
$$

So we can just apply this to our original policy-gradient expression:

$$
\begin{aligned}
\nabla_\theta J(\theta)
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right]\\
&= \mathbb{E}_{\tau\sim\pi_{\theta_{\mathrm{old}}}}\left[w(\tau)\,\sum_{t=0}^{T-1}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right]
\end{aligned}
$$

We can also define the ratio on the token-level:

$$
r_{t}(\theta) = \frac{\pi_{\theta}(a_t\mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t\mid s_t)}
$$

## CISPO

Actually, we basically already have enough to get the current SOTA RL algorithm, CISPO[^cispo]!

CISPO's loss is:

$$
J_{\mathrm{CISPO}}(\theta)
= \mathbb{E}_{(q,a)\sim\mathcal{D},\,\{o^i\}_{i=1}^G\sim\pi_{\theta_{\mathrm{old}}}(\cdot\mid q)}\left[
\frac{1}{\sum_{i=1}^G |o^i|}
\sum_{i=1}^G\sum_{t=1}^{|o^i|}
\mathrm{sg}\big(r_{i,t}(\theta)\big)\,\hat A_{i,t}\,\log \pi_\theta\big(o^i_t\mid q,o^i_{<t}\big)
\right]
$$

Note that we are averaging over groups here (the $i$ index) and over timesteps (number of tokens in a given rollout). $\mathrm{sg}$ stands for "stop gradient", and is used to avoid backpropagating through the logprobs used in computing the importance ratio $r$. $G$ is our group size (number of rollouts sharing a prompt), which is used to compute the advantage $\hat A$:

$$
\hat A_{i,t}
= \frac{R_i - \mathrm{mean}(\{R_j\}_{j=1}^G)}{\mathrm{std}(\{R_j\}_{j=1}^G)}
$$

Note that this is intuitively capturing exactly what we were doing before, but using the group estimates instead of a learned function for the value estimates.

## Other Advantage Estimates

Some other interesting advantage estimates:

1. **VinePPO**[^vineppo]: Use token-level Monte Carlo rollouts to estimate value. Incredibly expensive but arguably the best way to do it.
2. **GIGPO**[^gigpo]: Tie together similar states by just using token similarity. Works really well for agentic state-based tasks (e.g., navigating a web browser), where we have access to the underlying state and that state is simple.
3. **REINFORCE++**[^reinforcepp]: Just use the average reward in your batch as the value estimate! Makes sense if your tasks are all similar.
4. **RLOO**[^rloo]: Basically GRPO, but remove the standard deviation and use a leave-one-out approach instead of doing average over all samples.

<div class="aside">
<strong>Final comment</strong>

<p>You might wonder why using the reward from trajectories is valid to include in the baseline for GRPO and other baselines like REINFORCE++ — doesn't this include the current action? Actually, this is a special case that is fine!</p>

<p>Firstly, using <em>other</em> trajectories is completely valid, since they are completely independent of our current action (different samples entirely). But the reward of our current trajectory is the weird part. Let's consider using the average batch reward-to-go as a baseline:</p>

$$
b(s_t) \equiv \frac{1}{B}\sum_{n=1}^{B} G^n_t \quad\text{, where B is our batch size}
$$

Then:

$$
\begin{aligned}
\nabla_\theta J(\theta)
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G^x_t - b(s_t))\right] \text{, let $x$ be our current sample in the batch.}\\
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G^x_t - \frac{1}{B}\sum_{n=1}^{B} G^n_t)\right] \\
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G^x_t -  \frac{1}{B}G^x_t - \frac{1}{B}\sum_{n=1,\ne x}^{B}G^n_t)\right] \\
&= \mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(\frac{B-1}{B}G^x_t - \frac{1}{B}\sum_{n=1,\ne x}^{B}G^n_t)\right]
\end{aligned}
$$

<p>We know using $\frac{1}{B}\sum_{n=1,\ne x}^{B}G^n_t$ is fine as a baseline, so we just need to consider $\frac{B-1}{B}G^x_t$. It should be intuitively clear that this just scales down the gradient by $\frac{B-1}{B}$, and so does not bias the final result. Strictly, using a leave-one-out estimate as in RLOO is better to avoid this scaling, but it does not hurt!</p>

<p>Crucially, this only works because <em>we used the reward itself in the baselining</em>. Other functions involving $a_t$ would be invalid to use.</p>
</div>

And that's it! Thanks for listening!

---

## References

[^seita]: Seita, D. (2017). [Going Deeper Into Reinforcement Learning: Fundamentals of Policy Gradients](https://danieltakeshi.github.io/2017/03/28/going-deeper-into-reinforcement-learning-fundamentals-of-policy-gradients/).

[^cispo]: MiniMax et al. (2025). [MiniMax-M1: Scaling Test-Time Compute](https://arxiv.org/abs/2501.08313).

[^vineppo]: Kazemnejad et al. (2025). [VinePPO: Refining Credit Assignment](https://arxiv.org/abs/2410.01679).

[^gigpo]: Feng et al. (2025). [Grouping in Group Policy Optimization for LLM](https://arxiv.org/abs/2504.02763).

[^reinforcepp]: Hu et al. (2025). [REINFORCE++: Stabilizing Critic-Free Policy](https://arxiv.org/abs/2501.03262).

[^rloo]: Ahmadian et al. (2024). [Back to Basics: Revisiting REINFORCE Style Optimization](https://arxiv.org/abs/2402.14740).

See also: Weng, L. (2018). [Policy Gradient Algorithms](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/); Sutton & Barto (1998). *Reinforcement Learning: An Introduction (Chapter 13)*.