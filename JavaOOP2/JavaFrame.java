
import java.awt.*;
import java.awt.event.*;
public class JavaFrame{

	public static void main(String[] args){
		Frame f_property=new Frame("bit class demo");
		f_property.setSize(800,500);
		f_property.setLayout(null);
		f_property.setVisible(true);
		f_property.addWindowListener(new WindowAdapter()
		{
			public void windowClosing(WindowEvent e)
			{
				System.exit(0);
			}
		});
	}

}