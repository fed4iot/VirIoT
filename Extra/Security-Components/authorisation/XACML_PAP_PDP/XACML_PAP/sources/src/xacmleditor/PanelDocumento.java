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
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.io.*;
import java.util.Map;

/* *************************************************************************
 * Title: PanelDocumento
 *
 * Description:*//** This panel is used for setting up the document.
 *
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 *
 * @version 1.3
 ***************************************************************************/
public class PanelDocumento
    extends JPanel {

  private DefaultTreeModel miDTM;
  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JButton jbtnSelect = new JButton();
  JButton jbtnEditar = new JButton();

  String archivoActualEsquema;
  File archivoActualPolitica;
  PrintStream ps;
  DefaultMutableTreeNode node;
  ElementoXACML elem;
  String xmlns;

  public PanelDocumento() {
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  public PanelDocumento(File archivoActual, DefaultTreeModel d, PrintStream ps) {

    archivoActualPolitica = archivoActual;
    miDTM = d;
    this.ps = ps;
    try {
      jbInit();
    }
    catch (Exception exception) {
      exception.printStackTrace();
    }
  }

  private void jbInit() throws Exception {
    this.setLayout(new MiLayout());
    jlblId.setText("Schema:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jtxtId.setPreferredSize(new Dimension(400, 20));
    jtxtId.setLocation(105, 30);
    jtxtId.addKeyListener(new MiDocumentKeyAdapter(this));
    if (miDTM.getChildCount(miDTM.getRoot()) > 0) {
      DefaultMutableTreeNode node = (DefaultMutableTreeNode) ( (
          DefaultMutableTreeNode) (miDTM.getRoot())).getFirstChild();
      elem = (ElementoXACML) node.getUserObject();      
      xmlns = (String) elem.getAtributos().get("xmlns");
      String schema = (String) elem.getAtributos().get("xsi:schemaLocation");
      if (schema != null) {
        archivoActualEsquema = schema.substring(schema.indexOf(" ") + 1);
      }
    }
    if (archivoActualEsquema != null) {
      jtxtId.setText(archivoActualEsquema);
    }
    jbtnSelect.setText("..");
    jbtnSelect.setLocation(525, 30);
    jbtnSelect.setPreferredSize(new Dimension(40, 20));
    jbtnSelect.addActionListener(new MiActionDocumentAdapter(this));
    jbtnEditar.setText("Validate");
    jbtnEditar.setLocation(220, 60);
    jbtnEditar.setPreferredSize(new Dimension(100, 20));
    jbtnEditar.addActionListener(new MiActionDocumentAdapter(this));

    this.add(jlblId);
    this.add(jtxtId);
    this.add(jbtnSelect);
    this.add(jbtnEditar);
  }

  public void keyReleased(KeyEvent e) {
    if (e.getSource() == jtxtId) {
      archivoActualEsquema = jtxtId.getText();
      if(elem!=null){
        Map mapa = elem.getAtributos();
        actualizarSchemaLocation(mapa);
      }
    }
  }

  public void actionPerformed(ActionEvent e) {
    if (e.getSource() == jbtnSelect) {

      JFileChooser cuadroAbrir = new JFileChooser();
      cuadroAbrir.setMultiSelectionEnabled(false);
      if (archivoActualEsquema != null) {
        cuadroAbrir.setCurrentDirectory(CurrentPath.getInstancia().getCurrdir());
      }
      cuadroAbrir.setFileFilter(new XMLFileFilter("xsd"));
      if (cuadroAbrir.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
        File temporal = cuadroAbrir.getSelectedFile();
        if (!temporal.toString().endsWith(".xsd")) {
          JOptionPane.showMessageDialog(this,
                                        "The File isn't Schema *.xsd",
                                        "Error of Selected",
                                        JOptionPane.WARNING_MESSAGE);
          ps.println("The File isn't Schema *.xsd");

        }
        else {
          CurrentPath.getInstancia().setCurrdir(temporal.getParentFile());
          archivoActualEsquema = temporal.getAbsolutePath();
          jtxtId.setText(archivoActualEsquema);
          Map mapa = elem.getAtributos();
          actualizarSchemaLocation(mapa);
        }
      }
    }
    else if (e.getSource() == jbtnEditar) {
      if (miDTM.getChildCount(miDTM.getRoot()) <= 0) {
        JOptionPane.showMessageDialog(this,
                                      "The policy isn't initialized",
                                      "Error policy",
                                      JOptionPane.WARNING_MESSAGE);
        ps.println("The policy isn't initialized");

      }
      else {

        if (archivoActualEsquema == null) {
          JOptionPane.showMessageDialog(this,
                                        "You haven't selected any Schema *.xsd",
                                        "Error File not found",
                                        JOptionPane.WARNING_MESSAGE);
          ps.println("You haven't selected any Schema *.xsd");

        }
        else if (xmlns == null || xmlns.equals("")) {
          JOptionPane.showMessageDialog(this,
                                        "xmlns required in element: " +
                                        elem.getTipo(),
                                        "Error Attribute required",
                                        JOptionPane.WARNING_MESSAGE);
          ps.println("xmlns required in element: " + elem.getTipo());

        }
        else {
          JAXPValidator val = new JAXPValidator();
          AnalizadorSAX asax = new AnalizadorSAX();
          try {
            Map mapa = elem.getAtributos();
            mapa.remove("xmlns:xsi");
            mapa.remove("xsi:schemaLocation");
            mapa.put("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
            actualizarSchemaLocation(mapa);
            ByteArrayOutputStream os = new ByteArrayOutputStream();
            ps.println("Process policy document.");
            asax.procesaValidar( (DefaultMutableTreeNode) miDTM.getRoot(), os);
            InputStream is = new ByteArrayInputStream(os.toByteArray());

            String salida;
            if (!new File(archivoActualEsquema).isAbsolute() &&
                !archivoActualEsquema.startsWith("http:")) {
              salida = val.validator(is, CurrentPath.getInstancia().getCurrdir()
                                     + java.io.File.separator +
                                     archivoActualEsquema);
            }
            else {
              salida = val.validator(is, archivoActualEsquema);
            }
            ps.println(salida);
            ps.println("Validator finish");
          }
          catch (Exception exc) {
            ps.println("Error (Warnings): Schema not Locate");
            ps.println("Process Policy Document finished");
          }
        }
      }
    }
  }

  private void actualizarSchemaLocation(Map mapa) {
    if (archivoActualEsquema.startsWith("http:")) {
      mapa.put("xsi:schemaLocation",
               xmlns + " " + archivoActualEsquema);
    }
    else {
      mapa.put("xsi:schemaLocation",
               xmlns + " " + new File(archivoActualEsquema).getName());
    }

  }

}

class MiActionDocumentAdapter
    implements ActionListener {
  private PanelDocumento adaptee;

  MiActionDocumentAdapter(PanelDocumento adaptee) {
    this.adaptee = adaptee;
  }

  public void actionPerformed(ActionEvent e) {
    adaptee.actionPerformed(e);
  }
}

class MiDocumentKeyAdapter
    extends KeyAdapter {
  private PanelDocumento adaptee;

  MiDocumentKeyAdapter(PanelDocumento adaptee) {
    this.adaptee = adaptee;
  }

  public void keyReleased(KeyEvent e) {
    adaptee.keyReleased(e);
  }
}
