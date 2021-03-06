 /**
  *	Unit tests for all controller functions
  */
 import java.util.ArrayList;
 public class ServerTest
 {
 	public static void main (String[] args)
 	{
        boolean status = true;
        System.out.println("Jesse is on day " + ANDROID_SIDE.day("Jesse") + " of his period");
        if(!ANDROID_SIDE.toggle("Jesse")) {
            System.out.println("toggle called server code with wrong arguments");
            status = false;
        }
        String nextPeriod;
        nextPeriod = ANDROID_SIDE.predict("Jesse");
        if(nextPeriod == null) {
            System.out.println("predict not available");
            status = false;
        }
        
        System.out.println(nextPeriod);

        System.out.println("Jesse is on his period: " + ANDROID_SIDE.status("Jesse"));

        System.out.println("Jesse is on day " + ANDROID_SIDE.day("Jesse") + " of his period");

        System.out.println("Jesse's previous period was " + ANDROID_SIDE.prev("Jesse"));

        System.out.println("Our tip for Jesse is: " + ANDROID_SIDE.tip("Jesse"));

        ArrayList<PeriodCalendarEntry> entries = ANDROID_SIDE.get_all("Jesse");
        for(PeriodCalendarEntry entry : entries) {
            System.out.println(entry);
        }

        ArrayList<PeriodListEntry> listEntries = ANDROID_SIDE.get_list("Jesse");



        if(status) {
            System.out.println("All appears well");
        }
        
// 		// Test user signin and register
// 		User use = ServerCom.register("testUser", "testPass", "7144943046");
// 		String uid;
// 		if (use == null)
// 			uid = ServerCom.signIn("testUser", "testPass");
// 		else
// 			uid = use.getUID();
// 		System.out.println(uid);
//
// 		// Test creating or joining apartment
// 		String aid = ServerCom.createApartment(uid, "testApt");
// 		if (aid == null)
// 			aid = ServerCom.setApartmentID(uid, "testApt");
//
// 		// Test get apt id
// 		System.out.println(ServerCom.getApartmentID(uid));
//
// 		// Test adding / removing repeating tasks
// 		ServerCom.addTask(aid, "task1", 30, true);
// 		System.out.println(ServerCom.removeTask(aid, "task1", "testUser"));
// 		// Expect true because it is repeating
//
// 		// Test adding / removing single-time tasks
// 		ServerCom.addTask(aid, "task2", 30, false);
// 		System.out.println(ServerCom.removeTask(aid, "task2", "testUser"));
// 		// Expect false because it is not repeating
//
// 		// Get and print tasks
// 		Task[] taskList = ServerCom.getTasks(aid);
// 		System.out.println("TASKS:");
// 		for (Task indiv : taskList)
// 		{
// 			System.out.println(indiv.getDescription());
// 			System.out.println(indiv.getAssignee());
// 		}
	}

 }
