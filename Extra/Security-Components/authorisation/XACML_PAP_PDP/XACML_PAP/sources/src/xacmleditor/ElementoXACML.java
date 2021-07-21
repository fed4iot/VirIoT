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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Hashtable;
import java.util.Map;

/** This class represents an abstract XACML
 * Element being this class the root of all elements of the XACML
 * schema.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public abstract class ElementoXACML
    implements Cloneable {

  private Map atributos;
  private String tipo;
  private boolean vacio;
  private String contenido;

  public boolean esVacio() {
    return vacio;
  }

  public Map getAtributos() {
    return atributos;
  }

  public String getTipo() {
    return tipo;
  }

  public String getContenido() {
    return contenido;
  }

  protected void setAtributos(Map ht) {
    this.atributos = ht;
  }

  protected void setTipo(String tipo) {
    this.tipo = tipo;
  }

  public void setVacio(boolean v) {
    vacio = v;
  }

  public void setContenido(String contenido) {
    vacio = false;
    this.contenido = contenido;
  }

  public void addContenido(String contenido) {
    if (this.contenido == null) {
      setContenido(contenido);
    }
    else {
      this.contenido += contenido;
    }
  }

  public abstract String getID();

  public String toString() {
    String aux = "<" + tipo + " : " + getID();
    if (esVacio()) {
      return aux + "/>";
    }
    return aux + ">";
  }

  public static String[] getAllDataTypes() {
    String[] allDataTypes = {
        "http://www.w3.org/2001/XMLSchema#string",
        "http://www.w3.org/2001/XMLSchema#boolean",
        "http://www.w3.org/2001/XMLSchema#integer",
        "http://www.w3.org/2001/XMLSchema#double",
        "http://www.w3.org/2001/XMLSchema#time",
        "http://www.w3.org/2001/XMLSchema#date",
        "http://www.w3.org/2001/XMLSchema#dateTime",
        "http://www.w3.org/TR/2002/WD-xquery-operators-20020816#dayTimeDuration",
        "http://www.w3.org/TR/2002/WD-xquery-operators-20020816#yearMonthDuration",
        "http://www.w3.org/2001/XMLSchema#anyURI",
        "http://www.w3.org/2001/XMLSchema#hexBinary",
        "http://www.w3.org/2001/XMLSchema#base64Binary",
        "urn:oasis:names:tc:xacml:1.0:data-type:rfc822Name",
        "urn:oasis:names:tc:xacml:1.0:data-type:x500Name"};
    return allDataTypes;
  }

  public static String[] getAllPolicyCombiningAlgorithm() {
    String[] allPolicyCombiningAlgorithm = {
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:permit-overrides",
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:deny-overrides",
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:first-applicable",
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:only-one-applicable",
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:ordered-deny-overrides",
        "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:ordered-permit-overrides"};
    return allPolicyCombiningAlgorithm;
  }

  public static String[] getAllRuleCombiningAlgorithm() {
    String[] allRuleCombiningAlgorithm = {
        "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:permit-overrides",
        "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:deny-overrides",
        "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:first-applicable",
        "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:ordered-deny-overrides",
        "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:ordered-permit-overrides"};
    return allRuleCombiningAlgorithm;
  }

  public static String[] getAllPrefixesIdentifier() {
    String[] allPrefixesIdentifier = {
        "urn:oasis:names:tc:xacml:2.0",
        "urn:oasis:names:tc:xacml:2.0:conformance-test",
        "urn:oasis:names:tc:xacml:2.0:context",
        "urn:oasis:names:tc:xacml:2.0:example",
        "urn:oasis:names:tc:xacml:1.0:function",
        "urn:oasis:names:tc:xacml:2.0:function",
        "urn:oasis:names:tc:xacml:2.0:policy",
        "urn:oasis:names:tc:xacml:1.0:subject",
        "urn:oasis:names:tc:xacml:1.0:resource",
        "urn:oasis:names:tc:xacml:1.0:action",
        "urn:oasis:names:tc:xacml:1.0:environment",
        "urn:oasis:names:tc:xacml:1.0:status"};
    return allPrefixesIdentifier;
  }

  public static String[] getAllAttributeId() {
    String[] allAttributeId = {
        "urn:oasis:names:tc:xacml:1.0:subject:authn-locality:dns-name",
        "urn:oasis:names:tc:xacml:1.0:subject:authn-locality:ip-address",
        "urn:oasis:names:tc:xacml:1.0:subject:authentication-method",
        "urn:oasis:names:tc:xacml:1.0:subject:authentication-time",
        "urn:oasis:names:tc:xacml:1.0:subject:key-info",
        "urn:oasis:names:tc:xacml:1.0:subject:request-time",
        "urn:oasis:names:tc:xacml:1.0:subject:name-format",
        "urn:oasis:names:tc:xacml:1.0:subject:session-start-time",
        "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
        "urn:oasis:names:tc:xacml:1.0:subject:subject-id-qualifier",
        "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
        "urn:oasis:names:tc:xacml:1.0:subject-category:codebase",
        "urn:oasis:names:tc:xacml:1.0:subject-category:intermediary-subject",
        "urn:oasis:names:tc:xacml:1.0:subject-category:recipient-subject",
        "urn:oasis:names:tc:xacml:1.0:subject-category:requesting-machine",
        "urn:oasis:names:tc:xacml:1.0:resource:resource-location",
        "urn:oasis:names:tc:xacml:1.0:resource:xpath",
        "urn:oasis:names:tc:xacml:1.0:resource:resource-id",
        "urn:oasis:names:tc:xacml:2.0:resource:target-namespace",
        "urn:oasis:names:tc:xacml:1.0:resource:simple-file-name",
        "urn:oasis:names:tc:xacml:1.0:action:action-id",
        "urn:oasis:names:tc:xacml:1.0:action:implied-action",
        "urn:oasis:names:tc:xacml:1.0:environment:current-date",
        "urn:oasis:names:tc:xacml:1.0:environment:current-dateTime",
        "urn:oasis:names:tc:xacml:1.0:environment:current-time"
        // JR
        ,
        "urn:oasis:names:tc:xacml:2.0:subject:role",
        "urn:xadl:domain:name", 
		"urn:xadl:ArchTypes:ComponentType:id",
		"urn:xadl:ArchTypes:ConnectorType:id",
		"urn:xadl:archStructure:component:id",
		"urn:xadl:archStructure:connector:id",
		"urn:xadl:archStructure:link:point",
		"urn:xadl:archStructure:link:pointSource",
		"urn:xadl:archStructure:link:pointDestination",
		"urn:xadl:subject",		
		"urn:xadl:principal",		
		"urn:xadl:privilege",		
		"urn:xadl:subject:src",		
		"urn:xadl:principal:src",		
		"urn:xadl:privilege:src",		
		"urn:xadl:subject:dst",		
		"urn:xadl:principal:dst",		
		"urn:xadl:privilege:dst"		
        // JREND
    };
    return allAttributeId;
  }

  public static String[] getAllSchemas() {
    String[] allSchemas = {
         "urn:oasis:names:tc:xacml:2.0:policy:schema:os",
        "urn:oasis:names:tc:xacml:2.0:policy:schema:cd:04",        
        "urn:oasis:names:tc:xacml:1.0:policy"};
    return allSchemas;
  }

  public static String[] getAllParamName() {
    String[] allParamName = {"creater","priority","weight"};
        return allParamName;

    }
  public static String[] getAllEffects() {
    String[] allEffects = {
        "Permit",
        "Deny"};
    return allEffects;
  }

  public static String[] getAllFunctions() {
    String[] allFunctions = {
        "urn:oasis:names:tc:xacml:1.0:function:string-equal",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-equal",
        "urn:oasis:names:tc:xacml:1.0:function:integer-equal",
        "urn:oasis:names:tc:xacml:1.0:function:double-equal",
        "urn:oasis:names:tc:xacml:1.0:function:date-equal",
        "urn:oasis:names:tc:xacml:1.0:function:time-equal",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-equal",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-equal",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-equal",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-equal",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-equal",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-equal",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-equal",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-equal",
        "urn:oasis:names:tc:xacml:1.0:function:integer-add",
        "urn:oasis:names:tc:xacml:1.0:function:double-add",
        "urn:oasis:names:tc:xacml:1.0:function:integer-subtract",
        "urn:oasis:names:tc:xacml:1.0:function:double-subtract",
        "urn:oasis:names:tc:xacml:1.0:function:integer-multiply",
        "urn:oasis:names:tc:xacml:1.0:function:double-multiply",
        "urn:oasis:names:tc:xacml:1.0:function:integer-divide",
        "urn:oasis:names:tc:xacml:1.0:function:double-divide",
        "urn:oasis:names:tc:xacml:1.0:function:integer-mod",
        "urn:oasis:names:tc:xacml:1.0:function:integer-abs",
        "urn:oasis:names:tc:xacml:1.0:function:double-abs",
        "urn:oasis:names:tc:xacml:1.0:function:round",
        "urn:oasis:names:tc:xacml:1.0:function:floor",
        "urn:oasis:names:tc:xacml:1.0:function:string-normalize-space",
        "urn:oasis:names:tc:xacml:1.0:function:string-normalize-to-lower-case",
        "urn:oasis:names:tc:xacml:1.0:function:double-to-integer",
        "urn:oasis:names:tc:xacml:1.0:function:integer-to-double",
        "urn:oasis:names:tc:xacml:1.0:function:or",
        "urn:oasis:names:tc:xacml:1.0:function:and",
        "urn:oasis:names:tc:xacml:1.0:function:n-of",
        "urn:oasis:names:tc:xacml:1.0:function:not",
        "urn:oasis:names:tc:xacml:1.0:function:integer-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:integer-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:integer-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:integer-less-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:double-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:double-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:double-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:double-less-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-add-dayTimeDuration",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-add-yearMonthDuration",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-subtract-dayTimeDuration",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-subtract-yearMonthDuration",
        "urn:oasis:names:tc:xacml:1.0:function:date-add-yearMonthDuration",
        "urn:oasis:names:tc:xacml:1.0:function:date-subtract-yearMonthDuration",
        "urn:oasis:names:tc:xacml:1.0:function:string-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:string-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:string-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:string-less-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:time-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:time-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:time-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:time-less-than-or-equal",
        "urn:oasis:names:tc:xacml:2.0:function:time-in-range",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-less-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:date-greater-than",
        "urn:oasis:names:tc:xacml:1.0:function:date-greater-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:date-less-than",
        "urn:oasis:names:tc:xacml:1.0:function:date-less-than-or-equal",
        "urn:oasis:names:tc:xacml:1.0:function:string-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:string-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:string-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:string-bag",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-bag",
        "urn:oasis:names:tc:xacml:1.0:function:integer-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:integer-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:integer-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:integer-bag",
        "urn:oasis:names:tc:xacml:1.0:function:double-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:double-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:double-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:double-bag",
        "urn:oasis:names:tc:xacml:1.0:function:time-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:time-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:time-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:time-bag",
        "urn:oasis:names:tc:xacml:1.0:function:date-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:date-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:date-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:date-bag",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-bag",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-bag",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-bag",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-bag",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-bag",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-bag",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-bag",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-one-and-only",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-bag-size",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-is-in",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-bag",
        "urn:oasis:names:tc:xacml:2.0:function:string-concatenate",
        "urn:oasis:names:tc:xacml:2.0:function:uri-string-concatenate",
        "urn:oasis:names:tc:xacml:1.0:function:any-of",
        "urn:oasis:names:tc:xacml:1.0:function:all-of",
        "urn:oasis:names:tc:xacml:1.0:function:any-of-any",
        "urn:oasis:names:tc:xacml:1.0:function:all-of-any",
        "urn:oasis:names:tc:xacml:1.0:function:any-of-all",
        "urn:oasis:names:tc:xacml:1.0:function:all-of-all",
        "urn:oasis:names:tc:xacml:1.0:function:map",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-match",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-string-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-uri-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-ipAddress-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-dnsName-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-rfc822Name-match",
        "urn:oasis:names:tc:xacml:1.0:function:regexp-x500Name-match",
        "urn:oasis:names:tc:xacml:1.0:function:xpath-node-count",
        "urn:oasis:names:tc:xacml:1.0:function:xpath-node-equal",
        "urn:oasis:names:tc:xacml:1.0:function:xpath-node-match",
        "urn:oasis:names:tc:xacml:1.0:function:string-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:string-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:string-union",
        "urn:oasis:names:tc:xacml:1.0:function:string-subset",
        "urn:oasis:names:tc:xacml:1.0:function:string-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-union",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-subset",
        "urn:oasis:names:tc:xacml:1.0:function:boolean-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:integer-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:integer-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:integer-union",
        "urn:oasis:names:tc:xacml:1.0:function:integer-subset",
        "urn:oasis:names:tc:xacml:1.0:function:integer-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:double-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:double-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:double-union",
        "urn:oasis:names:tc:xacml:1.0:function:double-subset",
        "urn:oasis:names:tc:xacml:1.0:function:double-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:time-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:time-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:time-union",
        "urn:oasis:names:tc:xacml:1.0:function:time-subset",
        "urn:oasis:names:tc:xacml:1.0:function:time-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:date-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:date-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:date-union",
        "urn:oasis:names:tc:xacml:1.0:function:date-subset",
        "urn:oasis:names:tc:xacml:1.0:function:date-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-union",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-subset",
        "urn:oasis:names:tc:xacml:1.0:function:dateTime-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-union",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-subset",
        "urn:oasis:names:tc:xacml:1.0:function:anyURI-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-union",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-subset",
        "urn:oasis:names:tc:xacml:1.0:function:hexBinary-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-at-least-one-memberof",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-union",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-subset",
        "urn:oasis:names:tc:xacml:1.0:function:base64Binary-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-at-least-onemember-of",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-union",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-subset",
        "urn:oasis:names:tc:xacml:1.0:function:dayTimeDuration-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-at-least-onemember-of",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-union",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-subset",
        "urn:oasis:names:tc:xacml:1.0:function:yearMonthDuration-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-union",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-subset",
        "urn:oasis:names:tc:xacml:1.0:function:x500Name-set-equals",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-intersection",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-at-least-one-member-of",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-union",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-subset",
        "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-set-equals"};
    return allFunctions;
  }

  // JR
  public static String[] getPossibleAttributeValues() {
	    String[] possibleAttributeValues = {
	    		"urn:oasis:names:tc:xacml:2.0:actions:hasPrivilegesOfRole",
	    		"urn:oasis:names:tc:xacml:2.0:actions:enableRole",
	    		"urn:xadl:action:AddBrick",
	    		"urn:xadl:action:RemoveBrick",
	    		"urn:xadl:action:BeginBrick",
	    		"urn:xadl:action:EndBrick",
	    		"urn:xadl:action:AddWeld",
	    		"urn:xadl:action:RemoveWeld",
	    		"urn:xadl:action:RouteMessage",
	    		"urn:xadl:action:rbac:addUser",
	    		"urn:xadl:action:rbac:addRole",
	    		"urn:xadl:action:rbac:assignUser",
	    		"urn:xadl:action:Trust",
				"RouteMessage",
				"SecureManagedSystem"
	    };
	    return possibleAttributeValues;
  }
  // JREND

  public boolean isAllowedChild(ElementoXACML e) {
    if (this.getAllowedChild() == null) {
      return false;
    }
    ArrayList array = new ArrayList(Arrays.asList(getAllowedChild()));
    return array.contains(e.getTipo());
  }

  public abstract String[] getAllowedChild();

  public int getMinNumChild(ElementoXACML e) {
    int i;
    if (getAllObligatory() == null) {
      return 0;
    }
    for (i = 0; i < getAllObligatory().length; i++) {
      if (e.getTipo().equals(getAllObligatory()[i])) {
        return 1;
      }
    }
    return 0;
  }

  public int getMaxNumChild(ElementoXACML e) {
    int i;
    if (getAllowedChild() == null) {
      return 0;
    }
    for (i = 0; i < getAllowedChild().length; i++) {
      if (e.getTipo().equals(getAllowedChild()[i])) {
        return Integer.MAX_VALUE;
      }
    }
    return Integer.MAX_VALUE;
  }

  public int getPosicion(ElementoXACML e) {
    return 0;
  }


  public abstract String[] getAllObligatory();

  public Object clone() {
    ElementoXACML obj = null;
    obj = ElementoXACMLFactoryImpl.getInstance().
        obtenerElementoXACML(tipo, new Hashtable());
    obj.atributos.putAll(atributos);
    obj.setTipo(tipo);
    obj.setContenido(contenido);
    obj.setVacio(vacio);
    return obj;
  }

}
