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
import javax.swing.tree.DefaultMutableTreeNode;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.io.File;

/* ******************************************************************
 * Title: ReferencePanel
 *
 * Description: *//** This panel is used for setting up a Reference
 * element.
 *
 *
 * @author Alberto Jimenez Lazaro y Pablo Galera Morcillo
 * @version 1.3
 *******************************************************************/
public class ReferencePanel
    extends ElementPanel {

  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JButton jbtnSelect = new JButton();
  JButton jbtnEditar = new JButton();

  File archivoActual;

  public ReferencePanel(DefaultMutableTreeNode n) {
    super(n);
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  private void jbInit() throws Exception {
    this.setLayout(new MiLayout());
    jlblId.setText(elemento.getTipo() + ":");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jtxtId.setText(elemento.getContenido());
    jtxtId.setPreferredSize(new Dimension(300, 20));
    jtxtId.setLocation(165, 30);
    jtxtId.addKeyListener(new MiElementKeyAdapter(this));
    jbtnSelect.setText("..");
    jbtnSelect.setLocation(475, 30);
    jbtnSelect.setPreferredSize(new Dimension(40, 20));
    jbtnSelect.addActionListener(new MiElementActionAdapter(this));
    jbtnEditar.setText("Edit");
    jbtnEditar.setLocation(220, 60);
    jbtnEditar.setPreferredSize(new Dimension(100, 20));
    jbtnEditar.addActionListener(new MiElementActionAdapter(this));
    if(jtxtId.getText().equals("")) jbtnEditar.setEnabled(false);

    this.add(jlblId);
    this.add(jtxtId);
    this.add(jbtnSelect);
    this.add(jbtnEditar);

  }

  public void keyReleased(KeyEvent e) {
    elemento.setContenido(jtxtId.getText());
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }

  public void actionPerformed(ActionEvent e) {
    if (e.getSource() == jbtnSelect) {

      JFileChooser cuadroAbrir = new JFileChooser();
      cuadroAbrir.setMultiSelectionEnabled(false);
      if (archivoActual != null) {
        cuadroAbrir.setCurrentDirectory(archivoActual.getParentFile());
      }
      cuadroAbrir.setFileFilter(new XMLFileFilter("xml"));
      int returnVal = cuadroAbrir.showOpenDialog(this);
      archivoActual = cuadroAbrir.getSelectedFile();
      if (returnVal == JFileChooser.APPROVE_OPTION) {
       jtxtId.setText(archivoActual.toURI().toString());
       elemento.setContenido(jtxtId.getText());
       if(!jtxtId.getText().equals("")){
         jbtnEditar.setEnabled(true);
       }else jbtnEditar.setEnabled(false);
      }
    }
    else if(e.getSource() == jbtnEditar){
      try{
        PrincipalPolitica p;
        if(!new File(jtxtId.getText()).isAbsolute())
            //todo modificado el replace por el replaceAll para soportar 1.4
            p = new PrincipalPolitica(CurrentPath.getInstancia().getCurrdir()+jtxtId.getText().replaceAll("./",File.separator));
        else
          p = new PrincipalPolitica(jtxtId.getText());
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        Dimension frameSize = p.getSize();
        if (frameSize.height > screenSize.height) {
          frameSize.height = screenSize.height;
        }
        if (frameSize.width > screenSize.width) {
          frameSize.width = screenSize.width;
        }
        p.setLocation( (screenSize.width - frameSize.width) / 2,
                      (screenSize.height - frameSize.height) / 2);
        p.setVisible(true);
      }catch(Exception exc){
        exc.printStackTrace();
      }
    }
  }

}
