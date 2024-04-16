import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
import gradio as gr

# Set gemini pro as LLM

llm = ChatGoogleGenerativeAI(model = "gemini-pro",
                             verbose = True,
                             temperature = 0.5,
                             google_api_key = "AIzaSyDe9Je637KU4HId6GjEatcAYPRZkuR_Z8k")

duckduckgo_search = DuckDuckGoSearchRun()

def create_crewai_setup (age, gender, disease):
    # Define Agents
    fitness_expert = Agent(
        role = "Fitness Expert",
        goal = f"""Analyse the fitness requirements for a {age}-year-old {gender} with {disease} suggest
        execise routimes and fitness strategies
        """,
        backstory = f"""Expert at undersatnding fitness needs, age-specific requirements, and gender-specific considerations. Skilled in developing
        customized exercise routines and fitness strategies.
        """,
        verbose=True,
        llm = llm,
        allow_delegation = True,
        tools =[duckduckgo_search],
    )

    nutritionist= Agent(
        role = "Nutritionist",
        goal = f"""Analyse the nutritional requirements for a {age}-year-old {gender} with {disease} provide dietary recommendations.
        """,
        backstory = f"""Knowledgeable in nutrition for different age groups and gender, especially for individuals of {age} year old.
        Provide tailored dietart advice base on specific nutrional needs.
        """,
        verbose=True,
        llm = llm,
        allow_delegation = True,
        
    )


    
    doctor= Agent(
        role = "Doctor",
        goal = f"""Evaluate the overalll health consideartions for a {age}-year-pld {gender} with disease and provide recommendation for a healty lifestyle.
          Pass it on to the  disease_expert if you re not an expert of {disease}.
        """,
        backstory = f"""Medical professional experienced in assessimh overall health and well-beings. 
        Offers recommendations for a healhty lifestyle considering age, gender, and disease factors
        """,
        verbose=True,
        llm = llm,
        allow_delegation = True,
        
    )

    # Check if the perso has a disease
    if disease.lower() == "yes":
        disease_expert = Agent(
            role="Disease Expert",
            goal = f"""provide recommendations for managing {disease}.
            """,
            backstory = f""" Specialized in dealng with individuals having {disease}.
            Offers tailored advice for managing the specific health condition
            Do not prescribe medicines but only advice.
            """,
            verbose=True,
            llm = llm,
            allow_delegation = True,
        )
        disease_task = Task(
            description = f"""Provide recommendations fo managing {disease}.
                """,
            agent  =disease_expert,
            llm=llm
        )

        health_crew = Crew(
            agents = [fitness_expert, nutritionist, doctor, disease_expert],
            tasks = [task1, task2, task3, disease_task],
            verbose = 2,
            process = Process.sequential,
        )
    else:
        # Define Task without Disease disease_expert 
        task1 = Task(
            description=f"""Analyze the fitness requiremets for a {age}- year-old {gender}
                    Provide recommendation for exercise routines and fitness startegies.
                    """,
            agent= fitness_expert,
            llm=llm
        )
        task2 = Task(
            description = f"""Assess nutional requirements for {age} -year-old {gender}
            Provide dietary recommendations based on specific nutrional needs.
            Do not prescribe a medicine.

            """,
            agent=nutritionist,
            llm=llm
        )
        task3 = Task(
            description = f"""Evaluate overall health consideartions for {age}-year-old {gender}
            Provide recommendations for a healthy lifestyle.

            """,
            agent=doctor,
            llm=llm
        )

        health_crew = Crew(
            agents = [fitness_expert, nutritionist, doctor],
            tasks = [task1, task2, task3],
            verbose = 2,
            process = Process.sequential,
        )

    # Create and run the crew 
    crew_result = health_crew.kickoff()

    # Write "no disease" of user doesnt have a disease 
    if disease.lower() != "yes":
        crew_result += f"\n disease : {disease}"

    return crew_result

# Gradio Interface 
def run_crewai_app(age, gender, disease):
    crew_result =  create_crewai_setup(age, gender, disease)
    return crew_result

iface = gr.Interface(
    fn = run_crewai_app,
    inputs  = ["text", "text", "text"],
    outputs = "text",
    title = " Health, Nutrition and Fitness Analysis",
    description = "Enter Age, Gender and Disease (or 'no' if there is no disease) to anlyaze fitness, nutrition, and health startegies"
)
iface.launch()

      

