package blockchain;

import java.io.File;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import java.io.FileInputStream;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.odins.util.filemanagement.Read4mFile;

import com.google.gson.JsonObject;



public class Blockchain {

    private static String BC_Int = (System.getenv("BlockChain_integration") != null) ? System.getenv("BlockChain_integration") : "0";
    private static String BC_Conf = (System.getenv("BlockChain_configuration") != null) ? System.getenv("BlockChain_configuration") : "0";
    private static String BC_Prot = (System.getenv("BlockChain_protocol") != null) ? System.getenv("BlockChain_protocol") : "http";
    private static String BC_Dom = System.getenv("BlockChain_domain");
    private static String BC_IP = System.getenv("BlockChain_IP");
    private static String BC_Port = (System.getenv("BlockChain_port") != null) ? System.getenv("BlockChain_port") : "8000";
    private static String BC_GetRec = (System.getenv("BlockChain_get_resource") != null) ? System.getenv("BlockChain_get_resource") : "/policy/" + BC_Dom;
    private static String BC_PostRec = (System.getenv("BlockChain_post_resource") != null) ? System.getenv("BlockChain_post_resource") : "/policy/register";
    private static String BC_UpdRec = (System.getenv("BlockChain_update_resource") != null) ? System.getenv("BlockChain_update_resource") : "/policy/update";

    public static String generateURIFromResourceEnvironment(String resource) {
    
            return BC_Prot + "://" + BC_IP + ":" + BC_Port + resource;
    }

    private static final JsonObject BlockChainConf = Read4mFile.readJSONFile("/usr/local/tomcat/PAPConfigData/blockchain.conf");
    private static String DOMAIN     = (BC_Conf == "0") ? BlockChainConf.get("domain").getAsString() : BC_Dom;
    private static String GET_URL    = (BC_Conf == "0") ? generateURIFromResource("get_resource") : generateURIFromResourceEnvironment(BC_GetRec);
    private static String POST_URL   = (BC_Conf == "0") ? generateURIFromResource("post_resource") : generateURIFromResourceEnvironment(BC_PostRec);
    private static String UPDATE_URL = (BC_Conf == "0") ? generateURIFromResource("update_resource") : generateURIFromResourceEnvironment(BC_UpdRec);

    public static String generateURIFromResource(String resource) {
    
			return BlockChainConf.get("protocol").getAsString() + "://" + 
	    			 BlockChainConf.get("IP").getAsString() + ":" +
	    			 BlockChainConf.get("port").getAsString() + 
	    			 BlockChainConf.get(resource).getAsString();
    }

    
    public static String getCurrentHash() throws IOException {
    	 System.out.println("...");
         System.out.println("SEND GET request... to" + GET_URL);
         String responseGETFinal = sendGET(GET_URL);
            
         JSONParser parser = new JSONParser();
         try {
             JSONObject json = (JSONObject) parser.parse(responseGETFinal);
            
             String digestBlockchain = (String) json.get("digest");
             System.out.println("New HASH at BlockChain: " + digestBlockchain);
             return digestBlockchain;
            
         } catch (ParseException e) {
             // TODO Auto-generated catch block
             e.printStackTrace();
         }
         return "";
    }

    public static void registerOrUpdate(String POLICY_FILE) throws IOException {

        //***************** Obtain Hash value policy file in shaChecksum *****************
        File file = new File(POLICY_FILE);

        String shaChecksum = "";
       
        try {
            //Use SHA-256 algorithm
            MessageDigest shaDigest = MessageDigest.getInstance("SHA-256");

            //SHA-256 checksum
            shaChecksum = getFileChecksum(shaDigest, file);
       
           
        }
        catch(NoSuchAlgorithmException e) {
          // do proper exception handling
            System.err.println("I'm sorry, but SHA-256 is not a valid message digest algorithm");
            return;
        }
        //see checksum
        System.out.println("Original HASH at BlockChain: " + shaChecksum);
        System.out.println("...");
       
        //***************** Recover Original Hash value domain in Blockchain *****************
        System.out.println("SEND GET request... to" + GET_URL);
        String responseGET = sendGET(GET_URL);
       
        if (responseGET.length() == 0) {
            System.out.println("GET response: not worked/not found.");
           
            System.out.println("...");
           
            System.out.println("SEND POST - Register request... to" + POST_URL + "; Domain: " + DOMAIN) ;
            //If Hash value domain not found, REGISTER domain.
            String responsePOST = sendPOST(POST_URL, DOMAIN, shaChecksum);
           
            System.out.println("POST response: " + responsePOST);
           
        } else {
            System.out.println("GET response: " + responseGET);
           
            System.out.println("...");
            System.out.println("SEND POST - Update request...to" + UPDATE_URL + "; Domain: " + DOMAIN) ;
            //If Hash value domain found, UPDATE domain.
            String responseUPDATE = sendPOST(UPDATE_URL, DOMAIN, shaChecksum);
           
            System.out.println("POST response: " + responseUPDATE);
        }
       
        //***************** Recover Final Hash value domain in Blockchain *****************
        System.out.println("...");
        System.out.println("SEND GET request... to" + GET_URL);
        String responseGETFinal = sendGET(GET_URL);
           
        JSONParser parser = new JSONParser();
        try {
            JSONObject json = (JSONObject) parser.parse(responseGETFinal);
           
            String digestBlockchain = (String) json.get("digest");
            System.out.println("New HASH at BlockChain: " + digestBlockchain);
           
        } catch (ParseException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
   
    private static String getFileChecksum(MessageDigest digest, File file) throws IOException
    {
        //Get file input stream for reading the file content
        FileInputStream fis = new FileInputStream(file);
        
        //Create byte array to read data in chunks
        byte[] byteArray = new byte[1024];
        int bytesCount = 0;
         
        //Read file data and update in message digest
        while ((bytesCount = fis.read(byteArray)) != -1) {
            digest.update(byteArray, 0, bytesCount);
        };
        
        //close the stream; We don't need it now.
        fis.close();
        
        //Get the hash's bytes
        byte[] bytes = digest.digest();
        
        //This bytes[] has bytes in decimal format;
        //Convert it to hexadecimal format
        StringBuilder sb = new StringBuilder();
        for(int i=0; i< bytes.length ;i++)
        {
            sb.append(Integer.toString((bytes[i] & 0xff) + 0x100, 16).substring(1));
        }
        
        //return complete hash
       return sb.toString();
    }
   

    private static String sendGET(String Request_URL) throws IOException {
        URL obj = new URL(Request_URL);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("GET");
        int responseCode = con.getResponseCode();
        System.out.println("REQUEST Response Code :: " + responseCode);
       
        if (responseCode == HttpURLConnection.HTTP_OK) { // success
            BufferedReader in = new BufferedReader(new InputStreamReader(
                    con.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            // print result
            //System.out.println(response.toString());
            return response.toString();
        } else {
            //System.out.println("GET request not worked");
            return "";
        }
    }
   
    //REFERENCE:
    //https://github.com/eugenp/tutorials/blob/master/core-java-modules/core-java-networking-2/src/main/java/com/baeldung/urlconnection/PostJSONWithHttpURLConnection.java
    private static String sendPOST(String Request_URL, String domain, String digest) throws IOException {
        URL obj = new URL(Request_URL);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("POST");

        // For POST only - START
        con.setDoOutput(true);
       
        String jsonInputString = "{\"domain\": \"" + domain + "\", \"digest\": \"" + digest + "\"}";
        System.out.println("Body post: " + jsonInputString);
               
        try(OutputStream os = con.getOutputStream()){
            byte[] input = jsonInputString.getBytes("utf-8");
            os.write(input, 0, input.length);
            os.flush();
            os.close();
        }
       
        int responseCode = con.getResponseCode();
        System.out.println("REQUEST Response Code :: " + responseCode);

        if (responseCode == HttpURLConnection.HTTP_OK) { //success
            BufferedReader in = new BufferedReader(new InputStreamReader(
                    con.getInputStream(), "utf-8"));
            String inputLine;
            StringBuffer response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            //System.out.println(response.toString());
            return response.toString();
        } else {
            //System.out.println("POST request not worked");
            //return con.getResponseMessage();
            return "";
        }
    }

}
