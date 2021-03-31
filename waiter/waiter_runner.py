import click
import requests
import json
import os

WAITER_SERVER = "http://127.0.0.1:5000/"

@click.group()
def cli():
    click.echo("")

@cli.command()
@click.option('--email', prompt=True, confirmation_prompt=False,
              hide_input=False)
@click.option('--password', prompt=True, confirmation_prompt=True,
              hide_input=True)
def register(email,password):
    submit_data = {"email":email, "password":password}
    resp = requests.post(WAITER_SERVER+"auth/register",data=submit_data)

    if resp.status_code == 200:
        jsoned = resp.json()
        api_key = jsoned['api_key']
        with open("~/.WAITER", "wx") as f:
            f.write(api_key)
        print("Succesfully registered and logged in.")
    else:
        print("There was an error with registration, please try again.")

@cli.command()
@click.option('--email', prompt=True, confirmation_prompt=False,
              hide_input=False)
@click.option('--password', prompt=True, confirmation_prompt=False,
              hide_input=True)
def login(email,password):
    submit_data = {"email":email, "password":password}
    resp = requests.post(WAITER_SERVER+"auth/login",data=submit_data)
    if resp.status_code == 200:
        jsoned = resp.json()
        api_key = jsoned['api_key']
        with open(os.path.join("",".WAITER"),"w") as f:
            f.write(api_key)
        print("Succesfully logged in.")
    else:
        print("There was an error with login, please try again.")
    

if __name__ == "__main__":
    cli()