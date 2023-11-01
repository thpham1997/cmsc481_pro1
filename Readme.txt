a. Team details: UMBC ID, Name of both the team partners.
    OG52173 Stephen Lee
    XR25856 Thanh Pham
b. Brief description of application task and protocol being implemented.
    The application is a note memo application that is hosted on a server, with all communications done over TCP.
    The user can add, delete and view memos from the server using a client app.
c. Summary of your learning
    First, We learned how to design a simple communication protocol using TCP. The implementation was started with drawing FSM to brainstorm the protocol. By doing so, we could define the simple and efficient protocol for our ptoject. In addition, during the process, we had to modified the FSM many times as we needed to cover many edge and error cases. Second, we learn how to use python socket programming to implement the protocol. There is one point in the application that is worth mentioned is that the ability to keep track of byte streaming from the client to server. We were able to have the server to store and process the incoming byte. By doing so, the server can either give a success message or error message without discarding incomplete messages. Finally, we had the chance to use Sqlite for our database. Althought it was simple but we learn how to use it and request queries from that. Also, with that, we did not have to worry about database management for this simple application.
d. Challenges faced in doing the assignment and how did you address it.
    The first challenge we faced was the time permitted. Because the project was in the midterm duration, we had very small amount of time. Obviously, this project was not fully completed as we thought, but we managed to implemented by putting more time. The second obstacle was to to error handling situation. There were many cases that we need to cover so we did a tremendous amount of testing to make sure the application works properly. The third problem was to handle to byte streaming case. It took a big amount of time to implement annd test this feature in the application. We wrote a separate file to test and use a simple algorithm to tackle it.


Approximate duration (in days) spent in completing the assignment. 6 days
