# visium
Visium is a text to video genarator, but it does not genarate the video using some video llm, it uses llm to write code and to genarate videos using manim in 3Blue1Brown Style

----
# Roadmap Blog
I am building this project step by step now, so that I can go through every component of the project to optimise everything
## Install Manim and run official examples
- https://docs.manim.community/en/stable/installation/uv.html I followed this webpage , I think following will be useful for making a docker image , dont install textlive-full for making 3b1b videos we can work with base textlive

```bash
sudo apt install texlive-latex-base texlive-latex-extra texlive-fonts-extra texlive-fonts-recommended dvipng
sudo apt install build-essential python3.10-dev libcairo2-dev libpango1.0-dev
sudo apt install ffmpeg pkg-config
uv add manim
```
Thats it manim installation done atlast, wohhhhfffff
- 
