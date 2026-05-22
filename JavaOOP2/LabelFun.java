import java.awt.*;
import java.awt.event.*;
public class LabelFun{
	public static void main(String[] args){
		Frame	frame_property=new Frame("User Profile");
		Label first_name=new Label("First Name : Noah");
		Label last_name=new Label("Last Name: Karoney");
		Label gender=new Label("Gender : Male");
		/**
		 * .setBounds(padding-left,margin-top,width,heigth)
		 * 
		 * */
		first_name.setBounds(10,80,600,33);

		last_name.setBounds(10,110,600,30);
		gender.setBounds(10,140,600,30);


		frame_property.setSize(800,500);
		frame_property.setLayout(null);
		frame_property.setVisible(true);

		frame_property.addWindowListener(new WindowAdapter()
		{
			public void windowClosing(WindowEvent e)
			{
				System.exit(0);
			} 
		});
		frame_property.add(first_name);
		frame_property.add(last_name);
		frame_property.add(gender);

	}


}