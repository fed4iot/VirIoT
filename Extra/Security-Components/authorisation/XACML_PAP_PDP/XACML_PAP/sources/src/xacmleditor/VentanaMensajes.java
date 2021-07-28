/*
 * Copyright 2005, 2006 Alberto Jiménez Lázaro
 *                      Pablo Galera Morcillo (umu-xacml-editor-admin@dif.um.es)
 *                      Dpto. de Ingeniería de la Información y las Comunicaciones
 *                      (http://www.diic.um.es:8080/diic/index.jsp)
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
package xacmleditor;

import javax.swing.*;
import java.awt.*;
import java.io.OutputStream;
import java.io.PrintStream;

/* ****************************************************************
 * Title: VentanaMensajes
 *
 * Description: *//** It's a panel for showing output and error messages
 * produced during the program execution.
 *
 * @author Alberto Jimenez Lazaro
 * @version 1.3
 *****************************************************************/
public class VentanaMensajes
    extends JPanel{

  JTextArea jtxtMensajes = new JTextArea();
  JScrollPane jscrllPanel;
  private OutputStream out=new VMOutputStream(this);
  BorderLayout borderLayout1 = new BorderLayout();
  private PrintStream printStream;

  public VentanaMensajes() {
    try {
      jbInit();
	printStream=new PrintStream(out);
    }
    catch (Exception exception) {
      exception.printStackTrace();
    }
  }


  private void jbInit() throws Exception {
    this.setLayout(borderLayout1);
    this.add(jtxtMensajes,borderLayout1.CENTER);
  }
  class VMOutputStream extends OutputStream{

    private VentanaMensajes vm;

    public VMOutputStream(VentanaMensajes vm){
      this.vm=vm;
    }

    public void write(int a){
      byte []aux={(byte)a};
      vm.jtxtMensajes.setText(vm.jtxtMensajes.getText()+new String(aux));
      vm.jtxtMensajes.repaint();
    }
  }

  public PrintStream getPrintStream(){
	return printStream;
  }

  public OutputStream getOutputStream(){
    return out;
  }


}
