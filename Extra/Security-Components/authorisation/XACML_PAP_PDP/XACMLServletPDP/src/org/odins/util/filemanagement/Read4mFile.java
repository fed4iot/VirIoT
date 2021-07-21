package org.odins.util.filemanagement;


import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonSyntaxException;



/**
 * The purpose of this class is to provide the needed tools to read from files.
 * 
 * 	Current supported functions:
 * 	- Read raw data from a file and put the result in a byte array 
 *  - Read data from a json file and put the result in a JSONObject
 *  
 *  TODO:
 *  - To be completed with the needed functions to read from Files.
 * 
 * @author dgarcia@odins.es
 * 
 *
 */
public class Read4mFile {

	
	/**
	 * Read a file, which path is specified in filePath as a String and return the content in a byte array
	 * @param String filePath
	 * @return byte []
	 * @throws IOException
	 */
	public static byte[] readFile2ByteArray(String filePath) throws IOException {
		InputStream is = new FileInputStream(filePath);
		int size = is.available();
		byte[] content = new byte[size];
		is.read(content);

		is.close();
		return content;
	}

	/**
	 * Read a file, which path is specified in filePath as a String and the encoding as Charset, and return the content in a String
	 * @param filePath
	 * @param encoding
	 * @return String
	 * @throws IOException
	 */
	public static String readFile2String(String filePath, Charset encoding) throws IOException
	{
		
		File f = new File(filePath);
		//System.out.println(f.toString());
		
		if(f.exists() && !f.isDirectory()) { 
			byte[] encoded = Files.readAllBytes(Paths.get(filePath));
			return new String(encoded, encoding);
		}
		
		throw new IOException(" The file "+ filePath + " does not exists");

	}
	
	
	/**
	 * Given a jsonFilePath in String format, we read the content and return the value as JsonObject
	 * @param String jsonFilePath
	 * @return JsonObject
	 */
	public static JsonObject readJSONFile(String jsonFilePath) 
	{
		JsonParser parser 		= new JsonParser();
		
		try {
			return (JsonObject) parser.parse( readFile2String(	jsonFilePath, 
														Charset.defaultCharset())
											);
			
		} catch (JsonSyntaxException | IOException e) {			
			e.printStackTrace();
			System.exit(-1);
		}
		return null;
	}
	
	

}
