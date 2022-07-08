import os
import boto3
import awsgi

from uuid import uuid4
from flask import Flask, jsonify, request
from flask_cors import CORS
from boto3.dynamodb.conditions import Attr

app = Flask(__name__)
CORS(app)


BASE_ROUTE = "/tasks"

# some_key = os.environ["somekey"]

client = boto3.client("dynamodb")

TABLE_NAME = os.environ.get("STORAGE_TASKS_NAME")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


# @app.route(BASE_ROUTE + "/key", methods=["GET"])
# def get_some_key():
#     return jsonify(data=some_key)


@app.route(BASE_ROUTE + "/new", methods=["POST"])
def create_task():
    request_json = request.get_json()
    task_id = str(uuid4())
    description = request_json.get("description")
    user = request_json.get("user")

    response = table.put_item(
        Item={
            "id": task_id,
            "description": description,
            "user": user,
        },
    )
    print("******************", response)
    return jsonify(data=response)


@app.route(BASE_ROUTE + "/", methods=["GET"])
def list_tasks():
    return jsonify(data=client.scan(TableName=TABLE_NAME))


@app.route(BASE_ROUTE + "/<user>", methods=["GET"])
def get_tasks_by_user(user):
    print("USER", user)
    tasks = table.scan(FilterExpression=Attr("user").eq(user))
    print("TASKS", tasks["Items"])
    return jsonify(data=tasks["Items"])


@app.route(BASE_ROUTE + "/<task_id>", methods=["GET"])
def get_task(task_id):
    task = client.get_item(TableName=TABLE_NAME, Key={"id": {"S": task_id}})
    return jsonify(data=task)


@app.route(BASE_ROUTE + "/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    response = client.delete_item(TableName=TABLE_NAME, Key={"id": {"S": task_id}})
    print("DEL: ", response)
    return jsonify(message="task deleted")


@app.route(BASE_ROUTE + "/<task_id>", methods=["PUT"])
def update_task(task_id):
    response = client.update_item(
        TableName=TABLE_NAME,
        Key={"id": {"S": task_id}},
        UpdateExpression="SET #description = :description",
        ExpressionAttributeNames={"#description": "description"},
        ExpressionAttributeValues={
            ":description": {"S": request.json["description"]},
        },
    )
    print("PUT RESPONSE", response)
    return jsonify(message=response)


def handler(event, context):
    return awsgi.response(app, event, context)