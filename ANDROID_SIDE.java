/**
 *	This is a controller, following the MVC design pattern
 *
 *	This file handles communications between the app and the server
 *	It makes all the necessary HTTP requests to get or post data
 *	to the server.
 */

package com.example.joshua.livetogether;

import java.io.BufferedReader;
import java.io.*; 
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.*;

/**
 *	Controller class which handles server and app communications
 */
public class ServerCom
{
	// Define string constant
	public static final String HOST = "http://sdchargers.herokuapp.com/";


	/**
	 * This method will take a connection, send args, and return the response
	 */
	public static StringBuffer executeRequest (HttpURLConnection connection, String args) throws Exception
	{
		try {
			// Finish prepping request headers
		    connection.setUseCaches(false);
		    connection.setRequestProperty("Content-Language", "en-US");  
			connection.setRequestProperty("Content-Type",
				"application/x-www-form-urlencoded");

			// Handle arguments if there are any
			if (args != null)
			{
				// Prepare to send arguments
			    connection.setRequestProperty("Content-Length", 
			    	Integer.toString(args.getBytes().length));

			    //Send request
			    DataOutputStream wr = new DataOutputStream (
			        connection.getOutputStream());
			    wr.writeBytes(args);
			    wr.close();
			}

		    // Get error or success code
		    int responseCode = connection.getResponseCode();

		    //Get Response text
			BufferedReader in = new BufferedReader(
			        new InputStreamReader(connection.getInputStream()));
			String inputLine;
			StringBuffer response = new StringBuffer();

			// Read full response into string buffer
			while ((inputLine = in.readLine()) != null) {
				response.append(inputLine);
			}
			in.close();

			return response;
		}
		// Re-throw any errors to be caught in subsequent method
		catch (Exception e) { throw e; }
	}

	/**
	 * Allow user to sign in and get their User ID
	 */
	public static String signIn (String username, String password) {
		HttpURLConnection connection = null;

		// Define arguments
		username = "username=" + username;
		password = "password=" + password;

		String args = username + "&" + password;

		try {
			//Create connection
			URL url = new URL(HOST + "login/");
			connection = (HttpURLConnection)url.openConnection();
			connection.setRequestMethod("POST");
	    	connection.setDoOutput(true);

		    // Execute request with no args
			StringBuffer response = executeRequest (connection, args);	

			// ---------------------
			// PROCESS JSON RESPONSE
			JSONObject respJson = new JSONObject(response.toString());
			JSONObject idObj = respJson.getJSONObject("_id");
			String uid = idObj.getString("$oid");
			return uid;


		} catch (Exception e) {
			e.printStackTrace();
			return null;
	    // Ensure that the connection closes
		} finally {
			if(connection != null) {
				connection.disconnect();
			}
		}
	}



	/**
	 * Gets an array of tasks with descriptions and assignees 
	 */
	public static Task[] getTasks (String apt_id) {
	  HttpURLConnection connection = null;

	  try {
	    //Create connection
	    URL url = new URL(HOST + "tasks/" + apt_id);
	    connection = (HttpURLConnection)url.openConnection();
	    connection.setRequestMethod("GET");

	    // Execute request with no args
		StringBuffer response = executeRequest (connection, null);	

		// ---------------------
		// PROCESS JSON RESPONSE
		JSONObject respJson = new JSONObject(response.toString());
		JSONArray arr = respJson.getJSONArray("tasks");
		String[] descriptions = new String[arr.length()];
		String[] assignees = new String[arr.length()];
		Task[] toReturn = new Task[arr.length()];
		for (int i = 0; i < arr.length(); i++)
		{
			JSONObject cur = arr.getJSONObject(i);
			descriptions[i] = cur.getString("description");
			assignees[i] = cur.getString("assignee");
			toReturn[i] = new Task(assignees[i], descriptions[i]);
		}
 		return toReturn;

 		// Handle null errors on return
	  } catch (Exception e) {
	    e.printStackTrace();
	    return null;
	    // Ensure that the connection closes
	  } finally {
	    if(connection != null) {
	      connection.disconnect();
	    }
	  }
	}
}
