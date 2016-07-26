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
	 *  Register a new user
	 */
	public static User register (String username, String password, String phoneNum) {
		HttpURLConnection connection = null;

		// Prepare user registration info
		username = "username=" + username;
		password = "password=" + password;

		// Clean up the phone number
		if (phoneNum.length() < 10)
			return null;
		phoneNum = "+1" + phoneNum.substring(phoneNum.length()-10);		
		String phone = "phonenum=" + phoneNum;
		
		String args = username + "&" + password + "&" + phone;

		try {
			//Create connection
			URL url = new URL(HOST + "register/");
			connection = (HttpURLConnection)url.openConnection();
			connection.setRequestMethod("POST");
	    	connection.setDoOutput(true);

		    // Execute request with no args
			StringBuffer response = executeRequest (connection, args);	

			// ---------------------
			// PROCESS JSON RESPONSE -- wrap
			// If username was taken return null
			if (response.toString().equals("\"Username is already taken!\""))
				return null;

			JSONObject respJson = new JSONObject(response.toString());
			String uid = respJson.getJSONObject("_id").getString("$oid");
			int conf = respJson.getInt("confirm");
			User returned = new User(uid, conf);
			return returned;


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
	 * Allow user to set apartment ID based on their User ID 
	 */
	public static String setApartmentID (String userID, String aptName) {
		HttpURLConnection connection = null;

		// Define arguments
		aptName = "aptName=" + aptName;

		String args = aptName;

		try {
			//Create connection
			URL url = new URL(HOST + "join/" + userID);
			connection = (HttpURLConnection)url.openConnection();
			connection.setRequestMethod("POST");
	    	connection.setDoOutput(true);

		    // Execute request with no args
			StringBuffer response = executeRequest (connection, args);	

			// ---------------------
			// PROCESS JSON RESPONSE - return apartment ID
			JSONObject respJson = new JSONObject(response.toString());
			JSONObject idObj = respJson.getJSONObject("_id");
			String aid = idObj.getString("$oid");
			if (aid.equals(""))
				return null;
			return aid;

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
	 * Allow user to CREATE a new apartment and join it based on their User ID 
	 */
	public static String createApartment (String userID, String aptName) {
		HttpURLConnection connection = null;

		// Define arguments
		aptName = "aptName=" + aptName;

		String args = aptName;

		try {
			//Create connection
			URL url = new URL(HOST + "create/" + userID);
			connection = (HttpURLConnection)url.openConnection();
			connection.setRequestMethod("POST");
	    	connection.setDoOutput(true);
		
		    // Execute request with no args
			StringBuffer response = executeRequest (connection, args);		

			// Check for error conditions
			if (response.equals("\"Apartment name is already taken!\""))
				return null;

			// PROCESS JSON RESPONSE - return ID of new apt
			try {
				JSONObject respJson = new JSONObject(response.toString());
				String aid = respJson.getJSONObject("_id").getString("$oid");
				if (aid.equals(""))
					return null;
				return aid;
			}
			catch (Exception e)
			{
				return null;
			}

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
	 * Given a user ID, return the associated apartment ID
	 */
	public static String getApartmentID (String userID) {
		HttpURLConnection connection = null;

		try {
			//Create connection
			URL url = new URL(HOST + "users/"
				+ userID);
			connection = (HttpURLConnection)url.openConnection();
			connection.setRequestMethod("GET");
		
		    // Execute request with no args
			StringBuffer response = executeRequest (connection, null);		

			// ---------------------
			// PROCESS JSON RESPONSE
			JSONObject respJson = new JSONObject(response.toString());
			JSONObject apartment = respJson.getJSONObject("apartment");
			String aid = apartment.getString("$oid");
			return aid;

		// Make the compiler happy! and report errors...
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
	 * Given an apartment ID and a task string, add it to the list
	 */
	public static String addTask (String apt_id, String task, int workload, boolean oneTime) {
	  HttpURLConnection connection = null;  

	  // Define arguments
	  task = "description=" + task;
	  String repeating = "repeating=" + (oneTime ? 0 : 1);
	  String weight = "weight=" + workload;

	  String args = task + "&" + weight + "&" + repeating;

	  try {
	    //Create connection
	    URL url = new URL(HOST + "tasks/" + apt_id);
	    connection = (HttpURLConnection)url.openConnection();
	    connection.setRequestMethod("POST");
		connection.setDoOutput(true);

	    // Execute request with no args
		StringBuffer response = executeRequest (connection, args);		    
	    
 		return (response.toString());
	    
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
	 * REMOVE a task by apartment ID and, description, and assignee
	 */
	public static boolean removeTask (String apt_id, String desc,
		String assign)
	{
	  HttpURLConnection connection = null;  

	  // Define arguments
	  String descrip = "description=" + desc;
	  assign = "assignee=" + assign;

	  String args = descrip + "&" + assign;

	  try {
	    //Create connection
	    URL url = new URL(HOST + "tasks/" + apt_id);
	    connection = (HttpURLConnection)url.openConnection();
	    connection.setRequestMethod("DELETE");
	    connection.setDoOutput(true);

	    // Execute request with no args
		StringBuffer response = executeRequest (connection, args);	

		// Re-add task if it is a repeating task
		if (response != null)
		{
			try {
				int weight = Integer.parseInt(response.toString());
				addTask(apt_id, desc, weight, true);
				return true;
			}
			catch (Exception e) {}
		}

 		return false;
	    
	  } catch (Exception e) {
	    e.printStackTrace();
	    return false;
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
