---
layout: post
title: Setting Up Tensorflow 1.0 on AWS
---

## Setting Up Tensorflow 1.0 on AWS

This is more a post for me than anyone else, keeping the steps I used for future reference. I'm leaving it online in case anyone finds it useful, though I imagine there are far better walkthroughs and tutorials available.

Firstly, set up an AWS instance with a **p2.xlarge** machine with Ubuntu 16.04, with around 100gigs on the SSD storage. I'd also recommend requesting a spot instance to keep a cap on how much you're paying (to avoid nasty surprises). Just follow the steps on the amazon site and you should be fine! Connect to the machine via ssh or however you wish. I just ssh'ed in from terminal, but whatever works.

Now for the installation itself.
Run the following:
~~~
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install -y build-essential git python-pip libfreetype6-dev libxft-dev libncurses-dev libopenblas-dev gfortran python-matplotlib libblas-dev liblapack-dev libatlas-base-dev python-dev python-pydot linux-headers-generic linux-image-extra-virtual unzip python-numpy swig python-pandas python-sklearn unzip wget pkg-config zip g++ zlib1g-dev
~~~

This deals with all the requirements and some fun extras. Now we need to install the CUDA toolkit:
~~~
$ wget https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64-deb
$ sudo dpkg -i cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64.deb
$ sudo apt-get update
$ sudo apt-get install cuda
~~~
And then cuDNN, which requires making an account with Nvidia [here](https://developer.nvidia.com/accelerated-computing-developer). Once you've done this, download these to your local machine:
* cuDNN v5.1 **Runtime** Library for Ubuntu14.04 (Deb)
* cuDNN v5.1 **Developer** Library for Ubuntu14.04 (Deb)

You'll need to upload these to your amazon instance. I just use scp, in my local shell. Change the directories to wherever you downloaded the cuDNN files and where you want to place the files on your amazon instance.
~~~
$ scp -i <Your .pem file here> ~/Downloads/libcudnn5_5.1.10-1+cuda8.0_amd64.deb  <amazon instance>:~/
$ scp -i <Your .pem file here> ~/Downloads/libcudnn5-dev_5.1.10-1+cuda8.0_amd64.deb  <amazon instance>:~/
~~~

Once these have been uploaded, we need to install them. Run the following commands:
~~~
$ sudo dpkg -i libcudnn5_5.1.5-1+cuda8.0_amd64.deb
$ sudo dpkg -i libcudnn5-dev_5.1.5-1+cuda8.0_amd64.deb
~~~

Finally, we just need to configure the environment to use CUDA:
~~~
$ export CUDA_HOME=/usr/local/cuda
$ export CUDA_ROOT=/usr/local/cuda
$ export PATH=$PATH:$CUDA_ROOT/bin
$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_ROOT/lib64
~~~

Finally, we install pip and virtualenv:
~~~
$ sudo apt-get install python-pip python-dev python-virtualenv
~~~
We setup and activate the virtualenv:
~~~
$ virtualenv --system-site-packages <targetDirectory>
$ source ~/<targetDirectory>/bin/activate
~~~
Finally, we install Tensorflow (go for python 2.7 if in doubt):
~~~
$ pip install --upgrade Tensorflow-gpu  # for Python 2.7 and GPU
$ pip3 install --upgrade Tensorflow-gpu # for Python 3.3 and GPU
 ~~~

 If you run into errors, check out [here](https://www.Tensorflow.org/install/install_linux#CommonInstallationProblems) for the official docs. To verify your install, just run:
 ~~~
 $ python
 >> import Tensorflow
 ~~~

 If this happens without any issues, Tensorflow should be working on your AWS machine! hooray!

 As a final (I promise!) step, you can install tmux to allow your machine to run even when you are not actively connected:
 ~~~
 $ sudo apt-get install tmux
 $ tmux
 ~~~

 When you close and then reopen the window, just run ```tmux attach``` to enter back into the shell you were running before (I'd recommend testing this out if you're unsure it's working).

 Oh wait! As a final final side note, it's a good idea to clone the repositories of Tensorflow and its models if you want to play around with them, or follow a tutorial:

 ~~~
 $ git clone https://github.com/Tensorflow/Tensorflow.git
 $ git clone https://github.com/Tensorflow/models.git
 ~~~

 Okay, done, I promise. Now free to mess with this and have fun!! I'm still working on my first Tensorflow project as of the time of writing, and I hope whoever reads this has great success with their own projects :) . Mostly just because I love seeing cool tech things.
