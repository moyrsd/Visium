<div align="center" >
  <img width="20%" src="https://github.com/moyrsd/visium/blob/e5e2c6523c581858407be311516c8223fbfb7e91/frontend/public/logo3.png" alt="Visium logo">
</div>

<div align="center" >
  <p align="center">
    <a href="https://www.youtube.com/watch?v=lA1DLPX7X3M&list=PL8wn-1UB8mCBkF62Zfw4F0ZGLPi2PAnNP">View Demo</a>
    ·
    <a href="https://github.com/moyrsd/visium/issues">Report Bug</a>
    ·
    <a href="https://github.com/moyrsd/visium/issues">Request Feature</a>
  </p>
</div>
<div align="center" >
  <img width="100%" src="https://github.com/user-attachments/assets/b94852cb-4875-45ae-98ed-a9d4fc139f8b">
</div>

Visium is a text to video genarator, but it does not genarate the video using some video llm, it uses llm to write code and to genarate videos using manim in 3Blue1Brown Style

##  Features
- **Generate 3b1b style videos**
- **Convert pdfs into videos**
- **Edit clips of the video with natural language or code**

# Installation
- docker image coming up wait if someone is watching me incase

# Stack
- Fast Api for bacekend, Langraph for AI and agentic workflows, SQL alchemy for DB
- Next js for frontend, Shadcn for UI library


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


## Improving the coding Agent
- Agent code was becoming to big for readability so I refactored the code
- Many places the the video clips generated was not that proper, So I have given eye to our agent
- I am sending a frame of the video after it is rendered for visual review 
- This gives better results than just relying on syntax errors


## Audio
- I think audio governs the flow of the video
- The duration of audio given by tts engine gives you an idea how long the clips should be so I have generated audio files first using deepgram
- Shoutout to deepgram(Not sponsored, Hehe), But one of the voice matches same as Grant Sanderson 
- Also, I have written a script to download bgm of 3b1b 
- Now, I just have to stich audio video and do post processing 


# Video 
- Finally, putting it altogether, the last versions of perfect hopefully bugless videos will the in a temp file
- I am just stiching the videos
- For stiching first I am combining video with audio, so that video-audio mapping is there, then I am puting fadein fadeout filter for smoother video  
- Adding 3b1b bgms in the overall video,Done 
- We got a video

# Setting up the server 
- This is one of the most simple and straight foward part of the video, we just have to make APIs for already existing functions
- 
