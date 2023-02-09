from flask import Flask, request, jsonify, render_template, flash
import io
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

@app.route("/getkeyword", methods=['POST'])
def get_keyword():
    # credentials for clarifai
    metadata = (('authorization', f'Key 686ba95e9a1249f9be2844836cc1bb35'),)
    userDataObject = resources_pb2.UserAppIDSet(user_id='jiatotheyi', app_id='e7ae71583e8e46219285b8f5fbcfe5ab')           
    
    # get file from POST request body with key name "file"
    image = request.files['file']

    # convert image to bytes object to pass to clarifai
    bytesObj = ""
    with io.BytesIO() as output:
        image.save(output)
        bytesObj = output.getvalue()

    # pass bytes object and get results from model 
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id="general-image-detection",
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=bytesObj
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )

    # if there is an error, return the error
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        return jsonify(
            {
                "code": 500,
                "description": post_model_outputs_response.outputs[0].status.description,
                "details": post_model_outputs_response.outputs[0].status.details

            }
        ), 500


    # store response from clarifai into result
    result = post_model_outputs_response.outputs[0].data.regions

    # declare an empty list for filtering
    concepts = []
    
    # filter out concept names from the list to make sure there are no duplicates
    for concept in result:
        if concept.data.concepts[0].name not in concepts:
            concepts.append(concept.data.concepts[0].name) 

    # return list of keywords gotten back from clarifai
    if (len(concepts)!= 0):
        return jsonify(
            {
                "code": 200,
                "keywords": concepts
            }
        )


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
