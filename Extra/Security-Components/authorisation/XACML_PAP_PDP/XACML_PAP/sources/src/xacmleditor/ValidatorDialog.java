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
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.PrintStream;

/* ******************************************************************
 * Title: ValidatorDialog
 *
 * Description: *//** A dialog for doing the validation.
 *
 *
 * @author Alberto Jimenez Lazaro y Pablo Galera Morcillo
 * @version 1.3
 *******************************************************************/
public class ValidatorDialog
    extends JDialog {

  JLabel jlblIdPol = new JLabel();
  JTextField jtxtIdPol = new JTextField();
  JButton jbtnSelectPol = new JButton();
  JLabel jlblIdEsq = new JLabel();
  JTextField jtxtIdEsq = new JTextField();
  JButton jbtnSelectEsq = new JButton();
  File archivoActualPolitica;
  File archivoActualEsquema;
  JButton jbtnValidar = new JButton();
  PrintStream ps;

  public ValidatorDialog(PrintStream ps) {
    this.ps = ps;

    try {
      setDefaultCloseOperation(DISPOSE_ON_CLOSE);
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  private void jbInit() throws Exception {
      this.getContentPane().setLayout(new MiLayout());
      //this.setLayout(new MiLayout());
    setSize(new Dimension(525, 180));
    setTitle("Validator Schema");

    jlblIdPol.setText("Policy:");
    jlblIdPol.setBounds(new Rectangle(25, 30, 98, 20));
    jtxtIdPol.setEditable(false);
    jtxtIdPol.setBounds(new Rectangle(100, 30, 11, 20));
    jtxtIdPol.setPreferredSize(new Dimension(340, 20));
    jbtnSelectPol.setText("..");
    jbtnSelectPol.setLocation(450, 30);
    jbtnSelectPol.setPreferredSize(new Dimension(40, 20));
    jbtnSelectPol.addActionListener(new MiValidatorActionAdapter(this));
    jlblIdEsq.setText("Schema:");
    jlblIdEsq.setBounds(new Rectangle(25, 60, 98, 20));
    jtxtIdEsq.setEditable(false);
    jtxtIdEsq.setBounds(new Rectangle(100, 60, 11, 20));
    jtxtIdEsq.setPreferredSize(new Dimension(340, 20));
    jbtnSelectEsq.setText("..");
    jbtnSelectEsq.setLocation(450, 60);
    jbtnSelectEsq.setPreferredSize(new Dimension(40, 20));
    jbtnSelectEsq.addActionListener(new MiValidatorActionAdapter(this));
    jbtnValidar.setText("Validate");
    jbtnValidar.setLocation(220, 90);
    jbtnValidar.setPreferredSize(new Dimension(100, 20));
    jbtnValidar.addActionListener(new MiValidatorActionAdapter(this));

    this.getContentPane().add(jlblIdPol);
    this.getContentPane().add(jtxtIdPol);
    this.getContentPane().add(jbtnSelectPol);
    this.getContentPane().add(jlblIdEsq);
    this.getContentPane().add(jtxtIdEsq);
    this.getContentPane().add(jbtnSelectEsq);
    this.getContentPane().add(jbtnValidar);
  }

  public void actionPerformed(ActionEvent e) {
    if (e.getSource() == jbtnSelectPol) {
      JFileChooser cuadroAbrir = new JFileChooser();
      cuadroAbrir.setMultiSelectionEnabled(false);
      if (archivoActualPolitica != null) {
        cuadroAbrir.setCurrentDirectory(archivoActualPolitica.getParentFile());
      }

      cuadroAbrir.setFileFilter(new XMLFileFilter("xml"));
      if (cuadroAbrir.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
        File temporal = cuadroAbrir.getSelectedFile();

        if (!temporal.toString().endsWith(".xml")) {
          JOptionPane.showMessageDialog(this,
                                        "The open File is not a Policy *.xml",
                                        "Error of Selection",
                                        JOptionPane.WARNING_MESSAGE);
        }
        else {
          archivoActualPolitica=temporal;
          jtxtIdPol.setText(archivoActualPolitica.toURI().toString());
        }
      }

    }
    else if (e.getSource() == jbtnSelectEsq) {
      JFileChooser cuadroAbrir = new JFileChooser();
      cuadroAbrir.setMultiSelectionEnabled(false);
      if (archivoActualEsquema != null) {
        cuadroAbrir.setCurrentDirectory(archivoActualEsquema.getParentFile());
      }
      cuadroAbrir.setFileFilter(new XMLFileFilter("xsd"));
      if (cuadroAbrir.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
        File temporal = cuadroAbrir.getSelectedFile();
        if (!temporal.toString().endsWith(".xsd")) {
          JOptionPane.showMessageDialog(this,
                                        "The open File is not a Schema *.xsd",
                                        "Error of Selection",
                                        JOptionPane.WARNING_MESSAGE);
       ps.println("The open File is not a Schema *.xsd");

      }
        else {
          archivoActualEsquema=temporal;
          jtxtIdEsq.setText(archivoActualEsquema.toURI().toString());
        }
      }
    }
    else if (e.getSource() == jbtnValidar) {
      if (archivoActualPolitica == null) {
        JOptionPane.showMessageDialog(this,
                                      "You need to choose a Policy *.xml",
                                      "Error of incomplete Data",
                                      JOptionPane.WARNING_MESSAGE);
      ps.println("You need to choose a Policy *.xml");

      }
      else if (archivoActualEsquema == null) {
        JOptionPane.showMessageDialog(this,
                                      "You need to choose a Schema *.xsd",
                                      "Error of incomplete Data",
                                      JOptionPane.WARNING_MESSAGE);
       ps.println("You need to choose a Schema *.xsd");

      }
      else {
        JAXPValidator val= new JAXPValidator();
        String salida = val.validator(archivoActualPolitica.toURI().
                                                toString(),
                                                archivoActualEsquema.toURI().
                                                toString());
       ps.println(salida);

        JOptionPane.showMessageDialog(this, salida,
                                      "Validator finish",
                                      JOptionPane.INFORMATION_MESSAGE);
        ps.println("Validator finish");

      }
    }
  }
}

class MiValidatorActionAdapter
    implements ActionListener {
  private ValidatorDialog adaptee;

  MiValidatorActionAdapter(ValidatorDialog adaptee) {
    this.adaptee = adaptee;
  }

  public void actionPerformed(ActionEvent e) {
    adaptee.actionPerformed(e);
  }
}
