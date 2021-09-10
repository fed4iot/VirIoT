
/*
 * @(#)Policy.java
 *
 * Copyright 2003-2004 Sun Microsystems, Inc. All Rights Reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *   1. Redistribution of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 * 
 *   2. Redistribution in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *
 * Neither the name of Sun Microsystems, Inc. or the names of contributors may
 * be used to endorse or promote products derived from this software without
 * specific prior written permission.
 * 
 * This software is provided "AS IS," without a warranty of any kind. ALL
 * EXPRESS OR IMPLIED CONDITIONS, REPRESENTATIONS AND WARRANTIES, INCLUDING
 * ANY IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 * OR NON-INFRINGEMENT, ARE HEREBY EXCLUDED. SUN MICROSYSTEMS, INC. ("SUN")
 * AND ITS LICENSORS SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY LICENSEE
 * AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES. IN NO EVENT WILL SUN OR ITS LICENSORS BE LIABLE FOR ANY LOST
 * REVENUE, PROFIT OR DATA, OR FOR DIRECT, INDIRECT, SPECIAL, CONSEQUENTIAL,
 * INCIDENTAL OR PUNITIVE DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY
 * OF LIABILITY, ARISING OUT OF THE USE OF OR INABILITY TO USE THIS SOFTWARE,
 * EVEN IF SUN HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
 *
 * You acknowledge that this software is not designed or intended for use in
 * the design, construction, operation or maintenance of any nuclear facility.
 */

package com.sun.xacml;

import com.sun.xacml.combine.RuleCombiningAlgorithm;

import com.sun.xacml.ctx.Result;

import java.io.OutputStream;
import java.io.PrintStream;

import java.net.URI;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;


/**
 * Represents one of the two top-level constructs in XACML, the PolicyType.
 * This optionally contains rules, which in turn contain most of the logic of 
 * a policy.
 *
 * @since 1.0
 * @author Seth Proctor
 */
public class Policy extends AbstractPolicy
{

    /**
     * Creates a new <code>Policy</code> with only the required elements.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param target the <code>Target</code> for this policy
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg, Target target) {
        this(id, combiningAlg, null, target, null, null, null);
    }

    /**
     * Creates a new <code>Policy</code> with only the required elements
     * plus some rules.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param target the <code>Target</code> for this policy
     * @param rules a list of <code>Rule</code> objects
     *
     * @throws IllegalArgumentException if the <code>List</code> of rules
     *                                  contains an object that is not a
     *                                  <code>Rule</code>
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg, Target target,
                  List rules) {
        this(id, combiningAlg, null, target, null, rules, null);
    }

    /**
     * Creates a new <code>Policy</code> with the required elements plus
     * some rules and policy defaults.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param target the <code>Target</code> for this policy
     * @param defaultVersion the XPath version to use
     * @param rules a list of <code>Rule</code> objects
     *
     * @throws IllegalArgumentException if the <code>List</code> of rules
     *                                  contains an object that is not a
     *                                  <code>Rule</code>
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg, Target target,
                  String defaultVersion, List rules) {
        this(id, combiningAlg, null, target, defaultVersion, rules, null);
    }

    /**
     * Creates a new <code>Policy</code> with the required elements plus
     * some rules and a String description.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param description a <code>String</code> describing the policy
     * @param target the <code>Target</code> for this policy
     * @param rules a list of <code>Rule</code> objects
     *
     * @throws IllegalArgumentException if the <code>List</code> of rules
     *                                  contains an object that is not a
     *                                  <code>Rule</code>
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg,
                  String description, Target target, List rules) {
        this(id, combiningAlg, description, target, null, rules, null);
    }

    /**
     * Creates a new <code>Policy</code> with the required elements plus
     * some rules, a String description and policy defaults.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param description a <code>String</code> describing the policy
     * @param target the <code>Target</code> for this policy
     * @param defaultVersion the XPath version to use
     * @param rules a list of <code>Rule</code> objects
     *
     * @throws IllegalArgumentException if the <code>List</code> of rules
     *                                  contains an object that is not a
     *                                  <code>Rule</code>
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg,
                  String description, Target target, String defaultVersion,
                  List rules) {
        this(id, combiningAlg, description, target, defaultVersion, rules, 
             null);
    }

    /**
     * Creates a new <code>Policy</code> with the required elements plus
     * some rules, a String description, policy defaults, and obligations.
     *
     * @param id the policy identifier
     * @param combiningAlg the <code>CombiningAlgorithm</code> used on the
     *                     rules in this set
     * @param description a <code>String</code> describing the policy
     * @param target the <code>Target</code> for this policy
     * @param defaultVersion the XPath version to use
     * @param rules a list of <code>Rule</code> objects
     * @param obligations a set of <code>Obligations</code> objects
     *
     * @throws IllegalArgumentException if the <code>List</code> of rules
     *                                  contains an object that is not a
     *                                  <code>Rule</code>
     */
    public Policy(URI id, RuleCombiningAlgorithm combiningAlg,
                  String description, Target target, String defaultVersion,
                  List rules, Set obligations) {
        super(id, combiningAlg, description, target, defaultVersion,
              obligations);

        // check that the list contains only rules
        if (rules != null) {
            Iterator it = rules.iterator();
            while (it.hasNext()) {
                Object o = it.next();
                if (! (o instanceof Rule))
                    throw new IllegalArgumentException("non-Rule in rules");
            }
        }

        setChildren(rules);
    }
    
    /**
     * Creates a new Policy based on the given root node. This is 
     * private since every class is supposed to use a getInstance() method
     * to construct from a Node, but since we want some common code in the
     * parent class, we need this functionality in a constructor.
     */
    private Policy(Node root) throws ParsingException {
        super(root, "Policy", "RuleCombiningAlgId");

        List rules = new ArrayList();
        String xpathVersion = getDefaultVersion();

        NodeList children = root.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            if (child.getNodeName().equals("Rule"))
                rules.add(Rule.getInstance(child, xpathVersion));
        }

        setChildren(rules);
    }

    /**
     * Creates an instance of a <code>Policy</code> object based on a
     * DOM node. The node must be the root of PolicyType XML object,
     * otherwise an exception is thrown.
     *
     * @param root the DOM root of a PolicyType XML type
     *
     * @throws ParsingException if the PolicyType is invalid
     */
    public static Policy getInstance(Node root) throws ParsingException {
        // first off, check that it's the right kind of node
        if (! root.getNodeName().equals("Policy")) {
            throw new ParsingException("Cannot create Policy from root of " +
                                       "type " + root.getNodeName());
        }

        return new Policy(root);
    }

    /**
     * Encodes this <code>Policy</code> into its XML representation and writes
     * this encoding to the given <code>OutputStream</code> with no
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     */
    public void encode(OutputStream output) {
        encode(output, new Indenter(0));
    }

    /**
     * Encodes this <code>Policy</code> into its XML representation and writes
     * this encoding to the given <code>OutputStream</code> with
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     * @param indenter an object that creates indentation strings
     */
    public void encode(OutputStream output, Indenter indenter) {
        PrintStream out = new PrintStream(output);
        String indent = indenter.makeString();

        out.println(indent + "<Policy PolicyId=\"" + getId().toString() +
                    "\" RuleCombiningAlgId=\"" +
                    getCombiningAlg().getIdentifier().toString() +
                    "\">");
        
        indenter.in();
        String nextIndent = indenter.makeString();

        String description = getDescription();
        if (description != null)
            out.println(nextIndent + "<Description>" + description +
                        "</Description>");

        String version = getDefaultVersion();
        if (version != null)
            out.println("<PolicyDefaults><XPathVersion>" + version +
                        "</XPathVersion></PolicyDefaults>");

        encodeCommonElements(output, indenter);

        indenter.out();
        out.println(indent + "</Policy>");
    }

}
