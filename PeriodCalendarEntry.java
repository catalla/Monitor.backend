public class PeriodCalendarEntry {

    String date;
    double temp, heart;
    int mood;
    boolean onPeriod;

    public PeriodCalendarEntry(String date, double temp, double heart, 
            int mood, boolean onPeriod) {
        this.date = new String(date);
        this.temp = temp;
        this.heart = heart;
        this.mood = mood;
        this.onPeriod = onPeriod;
    }

    @Override
    public String toString() {
        return "Date = " + date + 
            "\nTemp = " + temp +
            "\nHeart= " + heart +
            "\nMood= " + mood +
            "\nonPeriod= " + onPeriod;
    }
}
