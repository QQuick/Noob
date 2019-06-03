// package websocket.client;

import java.net.URI;
import javax.websocket.*;

@ClientEndpoint
public class Jooc {
    private static Object waitLock = new Object ();
    
    @OnMessage
    public void onMessage( String message) {
       System.out.println ("Received msg: " + message);        
    }
    
    private static void  waitForTerminationSignal () {
        synchronized (waitLock) {
            try {
                waitLock.wait ();
            }
            catch (InterruptedException exception) {
                exception.printStackTrace ();
            }
        }
    }
    
    public static void main (String [] args) {
        WebSocketContainer container = null;//
        Session session = null;
        try{
            container = ContainerProvider.getWebSocketContainer (); 
            session = container.connectToServer (Jooc.class, URI.create ("ws://localhost:6666")); 
            session.getAsyncRemote () .sendText ("[\"register\", \"master\", \"ABN\"]");
            waitForTerminationSignal ();
        }
        catch (Exception exception) {
            exception.printStackTrace ();
        }
        finally {
            if (session != null) {
                try {
                    session.close ();
                }
                catch (Exception exception) {     
                    exception.printStackTrace ();
                }
            }         
        } 
    }
}
