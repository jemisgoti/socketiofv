from logging import debug
from flask import Flask, json, request,jsonify,render_template
from flask_socketio import SocketIO, close_room, join_room, leave_room, rooms, send
import firebase_admin
from firebase_admin import credentials,firestore

cred = credentials.Certificate('service_account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'mynameiskhanandiamnotterrorist'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('index.html')
    # return jsonify({"msg":"thank you aap mumbai nahi aa sakta"})

@app.route('/createRoom/',methods=['POST'])
def createRoom():
    try:
        data = request.get_json()
        roomID = data['roomID'] #room id will be one who is going to start the recording
        doctorID = data['doctorID']
        #get the data of available stream and append to it
        fireStore_data = db.collection('users').document(doctorID).get().to_dict()
        available_stream = fireStore_data['available_stream']
        # check whether id already exist or not
        for i in available_stream:
            if i == roomID:
                return jsonify({"msg":"Room already exist","roomID":i,"status":1})
        available_stream.append(roomID)
        db.collection('users').document(doctorID).set({"available_stream":available_stream})
        return jsonify({"msg":"Room created succesfully","status":1,"roomID":roomID})
    except Exception as e:
        return jsonify({"msg":"There was some prolem creating room","status":0})
    
@app.route('/removeRoom/',methods=['POST'])
def removeroom():
    try:
        data = request.get_json()
        doctorID = data['doctorID']
        roomID = data['roomID'] 
        fireStore_data = db.collection('users').document(doctorID).get().to_dict()
        available_stream = fireStore_data['available_stream']
        print(data)
        new_room = []
        for i in range(available_stream):
            if i != roomID:
                new_room.append(i)
        db.collection('users').document(doctorID).set({"available_stream":new_room})
        return jsonify({"msg":"Room remoev succesfully","status":1,"data":data})
    except Exception as e:
        return jsonify({"msg":"There was some prolem in removing room","status":0})


# @socketio.on('join_room')
@socketio.on('join_room')
def joinroom(data):
    app.logger.info("someone joined the room")
    join_room(data['roomID'])
    socketio.emit("recieve_message",data=data,room=data['roomID'])

@socketio.on('close_room')
def leaveroom(data):
    app.logger.info("Someone leave the room")
    close_room(data['roomID'])
    socketio.emit('recieve_message',data=data,room=data['roomID'])

@socketio.on('send_message')
def sendmessage(data):
    print(data)
    socketio.emit('recieve_message',data=data,room=data['roomID'])
    
@socketio.on('show_all_rooms')
def show_all_rooms(data):
    av_rooms = rooms()
    socketio.emit('recieve_message',data=av_rooms,rooms=data['roomID'])

if __name__ == "__main__":
    socketio.run(app,debug=True)