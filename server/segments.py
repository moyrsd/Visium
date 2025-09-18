from manim import *

class Intro(Scene):
    def construct(self):
        text = Text("Welcome to Visium")
        self.play(Write(text))
        self.wait(2)

class Formula(Scene):
    def construct(self):
        formula = MathTex(r"E = mc^2")
        self.play(Write(formula))
        self.wait(2)    

class Graph(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3], y_range=[-1, 1])
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        self.play(Create(axes), Create(sin_graph))
        self.wait(2)
