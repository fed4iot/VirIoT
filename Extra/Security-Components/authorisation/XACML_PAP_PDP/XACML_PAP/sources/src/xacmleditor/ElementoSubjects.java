
package xacmleditor;

import java.util.Map;

/** This class represents the XACML Subjects Element.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public class ElementoSubjects
    extends ElementoXACML {

  public static final String TIPO_SUBJECTS="Subjects";

  public ElementoSubjects(Map ht) {
    super.setTipo(TIPO_SUBJECTS);
    super.setAtributos(ht);
  }

  public String getID(){
    return "";
  }
  public boolean isUnico() {
    return true;
  }

  public String toString(){
    String aux="<"+getTipo();
    if(esVacio()) return aux+"/>";
    return aux+">";
  }

  public String[] getAllowedChild(){
     String[] allowedChild={
             // JR
         	"AnySubject",
         	// JREND
    		 "Subject"};
     return allowedChild;
  }

  public String[] getAllObligatory() {
  String[] AllObligatory = null;
  // JR
  		/*
  		 {
      	"AnySubject",
      "Subject"
       };*/
	// JREND
  return AllObligatory;
}


}
