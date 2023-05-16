
from flask import Flask, json, request
from flask_restful import Api, Resource, reqparse

import json
import os

from CPE import *

if __name__=='__main__':
    app = Flask(__name__)
    api = Api(app)


    cpe = CPE(password="areyouready?1")

    class CPEMeasures(Resource):
        def get(self,time):
            if (int(time) == -1):
                cpe.clear_stats()
                return 200
            if(int(time)>0):
                data, sig, tr = cpe.recordData(duration=int(time), delta=2,dataFormat="byGroup")
                #data, sig, tr, path = cpe.recordDataFile(duration=int(time), delta=2, filename = "prueba_60min")
    
    
                #data2 = json.dumps(data,skipkeys=True)
                print(data)
                data['traffic'].update(tr)
            else:
                data = cpe.get_traffic_stats().to_dict('records')[0]
                data.update(cpe.deviceSignalS())
                print(data)
            
            return data

        def post(self,time):
            parser = reqparse.RequestParser()
            parser.add_argument('filename')
            parser.add_argument('time')
            parser.add_argument('delta')
            parser.add_argument('reset')
            args = parser.parse_args()

            if(args['reset'] == None or args['reset'] == "True"):
                args['reset'] = True
            else:
                args['reset'] = False
            if(args['filename'] == None):
                data, sig, tr = cpe.recordData(restart = args['reset'], duration=int(args['time']), delta=int(args['delta']), dataFormat="byGroup")
            else:
                data, sig, tr, path = cpe.recordDataFile(restart = args['reset'], duration=int(args['time']), delta=int(args['delta']), filename=args['filename'])

            data['traffic'].update(tr)
            return data

    api.add_resource(CPEMeasures, "/CPE/<string:time>")
    app.run(host="0.0.0.0", port = 5000)