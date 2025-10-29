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
## JSON to video worker
- So I am first thinking of the idea to implement just one json file, cause LLM can make JSON very deterministically so if we create a JSON then create code and then create video from that all good
- Now, to run this at this stage just do after all normal uv stuff and run
```
python worker.py
```
## How the worker is working 
- load the the JSON object with already written code
- render the code and parallelise it simple
- we are using ProcessPoolExecutor and not asyncio cause, it helps to parallelise and create subprocesses inside the CPU unlike the asyncio which uses one thread only like Javascript
- then last important peice of the puzzle is subprocesses by which I can run CMD commands using python this is the best 

## Next is create a langraph workflow 
- The main problem I was facing was LLM is not able to code properly the things, until direcitions its fine but when it come to coding it does not work
- so I tried to implement an agentic workflow where one llm genarates codes and other llm reviewer checks code, on theory it should have worked but it gave disastrous results, the llm started making new manim apis which never existed 
- I am thinking to switch to simple boring slides, with no animation and naration how it works in NotebookLM videos of Google
- Fun Fact : Even NotebookLM cant prove pythagoras thorem visually, I was solving such an hard problem, the llm is the bottle neck my architecture is fine 

## Make Slides with manim
- To make slides the script nodes designs the dialouge and the visuals for static slides and then director improves the visuals to be more deterministic in 3b1b visual style
- Then the graph dynamically creates many coding agents which write code and reveiwes code until code quality and syntax correctness is matched 
- Finally all the independent workers populates the codes state in the main graph
- But the workers dont maintain order so I have send their index while intiating workers and finally sorting them
