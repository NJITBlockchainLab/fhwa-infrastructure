**Concept: Infrastructure as an Aries Agent**
In our system, the infrastructure plays a vital role as an Aries agent. But what does that mean exactly?

**What is Aries?**
Aries is an open-source project that provides a set of tools and libraries for building self-sovereign identity (SSI) solutions. It enables secure, peer-to-peer communication between parties while ensuring privacy and data ownership.

**Infrastructure as an Aries Agent**
In our context, the infrastructure refers to the network of physical elements such as road infrastructure, traffic lights, and other smart components deployed within an environment. By equipping these elements with Aries agent capabilities, we empower them to participate actively in the communication network.

**Integration with FHWA Mobile App Agent**
One of the key interactions in our system is between the infrastructure and the FHWA (Federal Highway Administration) mobile app agent deployed in vehicles. When a new instance of the FHWA mobile app agent starts up in a vehicle, it initiates a connection process with the infrastructure.

**Multi-Use Invitation**
The infrastructure exposes a multi-use invitation, essentially a shared access point for connecting with the infrastructure. This invitation allows multiple entities, such as vehicles running the FHWA mobile app agent, to establish connections with the infrastructure.

**Dedicated Connection**
Despite being a single common invitation, each application connecting to the infrastructure through this invitation obtains a dedicated connection. This means that once established, the FHWA mobile app agent has its unique channel of communication with the infrastructure.

**Benefits of Dedicated Connection**
By having a dedicated connection, the FHWA mobile app agent can seamlessly communicate with the infrastructure. This dedicated channel ensures reliability, security, and efficiency in message transmission between the vehicle and the infrastructure.

**Communication with Vehicles**
With these dedicated connections in place, the infrastructure gains the capability to communicate effectively with vehicles within the network. It can send messages, receive data, and coordinate actions, thereby enabling advanced functionalities such as traffic management, safety alerts, and more. By treating infrastructure as an Aries agent and establishing dedicated connections with vehicles, we create a robust and efficient communication framework that enhances the overall capabilities and intelligence of the transportation system.

**Steps to Run:**
1. Run the setup script in the main folder to install dependencies.

`./setup`

If using Windows follow steps in setup.txt.


Also run 

`pip install -r requirements.txt`

in the main folder.

2. 

If in Windows use Git Bash to run Shell scripts.

3. To run you have two options:
A. Run the program on the port 8054 of your public IP. Your public IP should allow inbound traffic on port 8054.
B. Open the port 8054 using ngrok. 

For A

Run

`./manage start-demo`

For B

I. Create .env file in ngrok folder
II. NGROK_AUTH_TOKEN=authtoken from ngrok
III. Run

`./start-ngrok.sh`


If in Windows use Git Bash to run Shell scripts.

IV. In the docker folder
Run

`./manage start-dev`


For both when 

               ::::::::::::::::::::::::::::::::::::::::::::::
               ::              infrastructure              ::
               ::                                          ::
               ::                                          ::
               :: Inbound Transports:                      ::
               ::                                          ::
               ::   - http://0.0.0.0:8051                  ::
               ::                                          ::
               :: Outbound Transports:                     ::
               ::                                          ::
               ::   - http                                 ::
               ::   - https                                ::
               ::                                          ::
               :: Public DID Information:                  ::
               ::                                          ::
               ::   - DID: HAKya82MNiU4WibuHFGx2f          ::
               ::                                          ::
               :: Administration API:                      ::
               ::                                          ::
               ::   - http://0.0.0.0:8054                  ::
               ::                                          ::
               ::                               ver: 0.9.0 ::
               ::::::::::::::::::::::::::::::::::::::::::::::
is an indication the program is running.

Note: To stop the program 
Run

`./manage stop`

To remove all containers and volume data

Run

`./manage rm`


4. Open a new tab to scripts folder. Go to invitation folder.
Run

For Windows

`python create-invitation.py`

For Linux

`python3 create-invitation.py`

For enabling s3
Create .env file and provide ACCESS_KEY and SECRET_KEY provided for infrastructure S3 bucket

5. Go to multicast folder 
There are 3 scripts for testing
I. Multicast: For sending complete data by selecting number of rows to send
II. Mutlicast Cyclic: Continously send data until explictly stopped
III. Mutlicast Events: Send data in range of the latitude and longtitude of the agent

For I

Run

`python multicast.py`

And specify the frequency and number of rows to send.


For II

Run

`python multicast_cyclic.py`

And specify the frequency and number of rows to send. Stop the program to stop sending data.


For III

Run

`python events.py`

And specify the latitude and longititude of the location to send.
For csv files change the placeholder csv files present in scripts/multicast/csv/Files
Keep the naming same eventlog.csv and pothole.csv

Run any of the 3 scripts using python


**NOTE**

If you run rm to remove docker container re-run the invitation program in scripts/invitation to generate new invitation and reset the old link.
