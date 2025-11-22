from crewai.flow.flow import Flow, listen, start, router, and_, or_

class FirstFlow(Flow):

    @start()
    def first_step(self):
        print("Hello")

    @listen(first_step)
    def second_step(self):
        print("world")

    @listen(first_step)
    def third_step(self):
        print("!")

    @listen(and_(second_step, third_step))
    def final_step(self):
        print("CrewAI")

    @router(final_step)
    def route(self):
        a = 1
        if a == 2:
            return 'even'
        else:
            return 'odd'
        
    @listen('even')
    def handle_even(self):
        print('even')

    @listen('odd')
    def handle_odd(self):
        print('odd')

flow = FirstFlow()

flow.plot()

# flow.kickoff()

