/*
 * Decompiled with CFR 0.148.
 * 
 * Could not load the following classes:
 *  org.jdom.Document
 *  org.jdom.input.DOMBuilder
 *  org.jdom.output.Format
 *  org.jdom.output.XMLOutputter
 *  xacmleditor.AnalizadorSAX
 *  xacmleditor.ConversorDOM
 *  xacmleditor.ElementoXACML
 *  xacmleditor.ElementoXACMLFactoryImpl
 *  xacmleditor.InsertarOrdenadoElemento
 */
package Umu_xacml_util;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.MutableTreeNode;
import javax.swing.tree.TreeModel;
import javax.swing.tree.TreeNode;
import org.jdom.Document;
import org.jdom.input.DOMBuilder;
import org.jdom.output.Format;
import org.jdom.output.XMLOutputter;
import org.w3c.dom.Node;
import org.xml.sax.SAXException;
import xacmleditor.AnalizadorSAX;
import xacmleditor.ConversorDOM;
import xacmleditor.ElementoXACML;
import xacmleditor.ElementoXACMLFactoryImpl;
import xacmleditor.InsertarOrdenadoElemento;

public class Umu_xacml_util {
    private DefaultMutableTreeNode raiz;
    private DefaultTreeModel miDTM = new DefaultTreeModel(new DefaultMutableTreeNode());
    private Hashtable<ElementoXACML, DefaultMutableTreeNode> treeNode = new Hashtable();

    public Umu_xacml_util() {
        this.raiz = new DefaultMutableTreeNode(new String("Policy Document"));
    }

    public Umu_xacml_util(Node node) throws IOException, SAXException {
        DOMBuilder domBuilder = new DOMBuilder();
        Document xacmlDoc = domBuilder.build((org.w3c.dom.Document)node);
        XMLOutputter outp = new XMLOutputter();
        outp.setFormat(Format.getCompactFormat());
        String message = outp.outputString(xacmlDoc);
        this.createTree(message);
    }

    public Umu_xacml_util(String xacml) throws IOException, SAXException {
        this.createTree(xacml);
    }

    private void createTree(String xacml) throws IOException, SAXException {
        AnalizadorSAX asax = new AnalizadorSAX();
        DefaultTreeModel DTM = (DefaultTreeModel)asax.analizarFromString(xacml);
        this.raiz = (DefaultMutableTreeNode)DTM.getRoot();
        Enumeration enumeration = this.raiz.preorderEnumeration();
        while (enumeration.hasMoreElements()) {
            DefaultMutableTreeNode node = (DefaultMutableTreeNode)enumeration.nextElement();
            if (!(node.getUserObject() instanceof ElementoXACML)) continue;
            ElementoXACML elementoXACML = (ElementoXACML)node.getUserObject();
            this.treeNode.put(elementoXACML, node);
        }
    }

    public void insertChild(ElementoXACML father, Umu_xacml_util child) {
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        this.insertaNodos(padreNode, child.treeNode.get((Object)child.getPrincipal()));
    }

    private void insertaNodos(DefaultMutableTreeNode father, DefaultMutableTreeNode child) {
        ElementoXACML elementoXACML = (ElementoXACML)child.getUserObject();
        DefaultMutableTreeNode hijoNode = this.insertaNodo(elementoXACML, father);
        ElementoXACML elementoxacml = (ElementoXACML)hijoNode.getUserObject();
        this.treeNode.put(elementoxacml, hijoNode);
        Enumeration en = child.children();
        while (en.hasMoreElements()) {
            DefaultMutableTreeNode grandSon = (DefaultMutableTreeNode)en.nextElement();
            this.insertaNodos(hijoNode, grandSon);
        }
    }

    public ElementoXACML createPrincipal(String type) {
        DefaultMutableTreeNode policyElement = this.crearNodos(type, this.raiz);
        ElementoXACML elementoXACML = (ElementoXACML)policyElement.getUserObject();
        this.treeNode.put(elementoXACML, policyElement);
        return elementoXACML;
    }

    public ElementoXACML getPrincipal() {
        DefaultMutableTreeNode policyElement = (DefaultMutableTreeNode)this.raiz.getFirstChild();
        return (ElementoXACML)policyElement.getUserObject();
    }

    public ElementoXACML createChild(ElementoXACML father, String type) {
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        DefaultMutableTreeNode hijoNode = this.crearNodos(type, padreNode);
        ElementoXACML elementoxacml = (ElementoXACML)hijoNode.getUserObject();
        this.treeNode.put(elementoxacml, hijoNode);
        return elementoxacml;
    }

    public List<ElementoXACML> getChildren(ElementoXACML father) {
        ArrayList<ElementoXACML> childList = new ArrayList<ElementoXACML>();
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        Enumeration children = padreNode.children();
        while (children.hasMoreElements()) {
            DefaultMutableTreeNode element = (DefaultMutableTreeNode)children.nextElement();
            childList.add((ElementoXACML)element.getUserObject());
        }
        return childList;
    }

    public List<ElementoXACML> getChildren(ElementoXACML father, String tipo) {
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        ArrayList<ElementoXACML> childList = new ArrayList<ElementoXACML>();
        for (DefaultMutableTreeNode node : this.getChildrenElements(padreNode, tipo)) {
            childList.add((ElementoXACML)node.getUserObject());
        }
        return childList;
    }

    public ElementoXACML getChild(ElementoXACML father, String tipo) {
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        DefaultMutableTreeNode child = this.getChildElement(padreNode, tipo);
        if (child != null) {
            return (ElementoXACML)child.getUserObject();
        }
        return null;
    }

    public void removeChild(ElementoXACML father, ElementoXACML child) {
        DefaultMutableTreeNode padreNode = this.treeNode.get((Object)father);
        DefaultMutableTreeNode childNode = this.treeNode.get((Object)child);
        padreNode.remove(childNode);
    }

    private DefaultMutableTreeNode crearNodos(String s, DefaultMutableTreeNode nodo) {
        ElementoXACML aux = ElementoXACMLFactoryImpl.getInstance().obtenerElementoXACML(s, new Hashtable());
        aux.setVacio(true);
        DefaultMutableTreeNode naux = new DefaultMutableTreeNode((Object)aux);
        if (nodo.getUserObject() instanceof ElementoXACML) {
            InsertarOrdenadoElemento ioe = new InsertarOrdenadoElemento(nodo, naux);
            ioe.ordenarInsercion();
            int pos = ioe.getPosicion();
            this.miDTM.insertNodeInto(naux, nodo, pos);
        } else {
            this.miDTM.insertNodeInto(naux, nodo, 0);
        }
        if (nodo.getUserObject() instanceof ElementoXACML) {
            this.miDTM.reload(nodo);
        } else {
            this.miDTM.reload();
        }
        return naux;
    }

    private DefaultMutableTreeNode insertaNodo(ElementoXACML elementoXACML, DefaultMutableTreeNode nodo) {
        DefaultMutableTreeNode naux = new DefaultMutableTreeNode((Object)elementoXACML);
        if (nodo.getUserObject() instanceof ElementoXACML) {
            InsertarOrdenadoElemento ioe = new InsertarOrdenadoElemento(nodo, naux);
            ioe.ordenarInsercion();
            int pos = ioe.getPosicion();
            this.miDTM.insertNodeInto(naux, nodo, pos);
        } else {
            this.miDTM.insertNodeInto(naux, nodo, 0);
        }
        if (nodo.getUserObject() instanceof ElementoXACML) {
            this.miDTM.reload(nodo);
        } else {
            this.miDTM.reload();
        }
        return naux;
    }

    private DefaultMutableTreeNode getChildElement(DefaultMutableTreeNode ruleElement, String tipo) {
        Enumeration children = ruleElement.children();
        while (children.hasMoreElements()) {
            DefaultMutableTreeNode element = (DefaultMutableTreeNode)children.nextElement();
            if (!((ElementoXACML)element.getUserObject()).getTipo().equals(tipo)) continue;
            return element;
        }
        return null;
    }

    private List<DefaultMutableTreeNode> getChildrenElements(DefaultMutableTreeNode policyElement, String tipo) {
        ArrayList<DefaultMutableTreeNode> rules = new ArrayList<DefaultMutableTreeNode>();
        Enumeration children = policyElement.children();
        while (children.hasMoreElements()) {
            DefaultMutableTreeNode element = (DefaultMutableTreeNode)children.nextElement();
            if (!((ElementoXACML)element.getUserObject()).getTipo().equals(tipo)) continue;
            rules.add(element);
        }
        return rules;
    }

    public org.w3c.dom.Document getDocument() {
        return ConversorDOM.convierte((DefaultMutableTreeNode)this.raiz);
    }

    public String toString() {
        org.w3c.dom.Document document = this.getDocument();
        DOMBuilder builder = new DOMBuilder();
        Document jdomDoc = builder.build(document);
        XMLOutputter outputter = new XMLOutputter(Format.getPrettyFormat());
        String messageOut = outputter.outputString(jdomDoc);
        return messageOut;
    }
}
