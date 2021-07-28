
/*
 * @(#)Apply.java
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

package com.sun.xacml.cond;

import com.sun.xacml.EvaluationCtx;
import com.sun.xacml.Indenter;
import com.sun.xacml.ParsingException;
import com.sun.xacml.UnknownIdentifierException;

import com.sun.xacml.attr.AttributeDesignator;
import com.sun.xacml.attr.AttributeFactory;
import com.sun.xacml.attr.AttributeSelector;
import com.sun.xacml.attr.AttributeValue;

import java.io.OutputStream;
import java.io.PrintStream;

import java.net.URI;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;


/**
 * Represents the XACML ApplyType and ConditionType XML types.
 *
 * @since 1.0
 * @author Seth Proctor
 */
public class Apply implements Evaluatable
{

    // the function used to evaluate the contents of the apply
    private Function function;

    // the paramaters to the function...ie, the contents of the apply
    private List evals;

    // an apply may have an entry that's a function for bag operations
    private Function bagFunction;

    // whether or not this is a condition
    private boolean isCondition;

    /**
     * Constructs an <code>Apply</code> object. Throws an
     * <code>IllegalArgumentException</code> if the given parameter list
     * isn't valid for the given function.
     *
     * @param function the <code>Function</code> to use in evaluating the
     *                 elements in the apply
     * @param evals the contents of the apply which will be the parameters
     *              to the function, each of which is an
     *              <code>Evaluatable</code>
     * @param isCondition true if this <code>Apply</code> is a Condition,
     *                    false otherwise
     */
    public Apply(Function function, List evals, boolean isCondition)
        throws IllegalArgumentException
    {
        this(function, evals, null, isCondition);
    }

    /**
     * Constructs an <code>Apply</code> object that contains a higher-order
     * bag function. Throws an <code>IllegalArgumentException</code> if the
     * given parameter list isn't valid for the given function.
     * 
     * @param function the <code>Function</code> to use in evaluating the
     *                 elements in the apply
     * @param evals the contents of the apply which will be the parameters
     *              to the function, each of which is an
     *              <code>Evaluatable</code>
     * @param bagFunction the higher-order function to use
     * @param isCondition true if this <code>Apply</code> is a Condition,
     *                    false otherwise
     */
    public Apply(Function function, List evals, Function bagFunction,
                 boolean isCondition)
        throws IllegalArgumentException
    {
        // check that the given inputs work for the function
        List inputs = evals;
        if (bagFunction != null) {
            inputs = new ArrayList();
            inputs.add(bagFunction);
            inputs.addAll(evals);
        }
        function.checkInputs(inputs);

        // if everything checks out, then store the inputs
        this.function = function;
        this.evals = Collections.unmodifiableList(new ArrayList(evals));
        this.bagFunction = bagFunction;
        this.isCondition = isCondition;
    }
    
    /**
     * Returns an instance of an <code>Apply</code> based on the given DOM
     * root node. This will actually return a special kind of
     * <code>Apply</code>, namely an XML ConditionType, which is the root
     * of the condition logic in a RuleType. A ConditionType is the same
     * as an ApplyType except that it must use a FunctionId that returns
     * a boolean value.
     * 
     * @param root the DOM root of a ConditionType XML type
     * @param xpathVersion the XPath version to use in any selectors or XPath
     *                     functions, or null if this is unspecified (ie, not
     *                     supplied in the defaults section of the policy)
     *
     * @throws ParsingException if this is not a valid ConditionType
     */
    public static Apply getConditionInstance(Node root, String xpathVersion)
        throws ParsingException
    {
        return getInstance(root, FunctionFactory.getConditionInstance(), true,
                           xpathVersion);
    }

    /**
     * Returns an instance of <code>Apply</code> based on the given DOM root.
     * 
     * @param root the DOM root of an ApplyType XML type
     * @param xpathVersion the XPath version to use in any selectors or XPath
     *                     functions, or null if this is unspecified (ie, not
     *                     supplied in the defaults section of the policy)
     *
     * @throws ParsingException if this is not a valid ApplyType
     */
    public static Apply getInstance(Node root, String xpathVersion)
        throws ParsingException
    {
        return getInstance(root, FunctionFactory.getGeneralInstance(), false,
                           xpathVersion);
    }

    /**
     * This is a helper method that is called by the two getInstance
     * methods. It takes a factory so we know that we're getting the right
     * kind of function.
     */
    private static Apply getInstance(Node root, FunctionFactory factory,
                                     boolean isCondition, String xpathVersion)
        throws ParsingException
    {
        Function function = getFunction(root, xpathVersion, factory);
        Function bagFunction = null;
        List evals = new ArrayList();
        
        AttributeFactory attrFactory = AttributeFactory.getInstance();

        NodeList nodes = root.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            String name = node.getNodeName();

            if (name.equals("Apply")) {
                evals.add(Apply.getInstance(node, xpathVersion));
            } else if (name.equals("AttributeValue")) {
                try {
                    evals.add(attrFactory.createValue(node));
                } catch (UnknownIdentifierException uie) {
                    throw new ParsingException("Unknown DataType", uie);
                }
            } else if (name.equals("SubjectAttributeDesignator")) {
                evals.add(AttributeDesignator.
                          getInstance(node,
                                      AttributeDesignator.SUBJECT_TARGET));
            } else if (name.equals("ResourceAttributeDesignator")) {
                evals.add(AttributeDesignator.
                          getInstance(node,
                                      AttributeDesignator.RESOURCE_TARGET));
            } else if (name.equals("ActionAttributeDesignator")) {
                evals.add(AttributeDesignator.
                          getInstance(node,
                                      AttributeDesignator.ACTION_TARGET));
            } else if (name.equals("EnvironmentAttributeDesignator")) {
                evals.add(AttributeDesignator.
                          getInstance(node,
                                      AttributeDesignator.ENVIRONMENT_TARGET));
            } else if (name.equals("AttributeSelector")) {
                evals.add(AttributeSelector.getInstance(node, xpathVersion));
            } else if (name.equals("Function")) {
                // while the schema doesn't enforce this, it's illegal to
                // have more than one FunctionType in a given ApplyType
                if (bagFunction != null)
                    throw new ParsingException("Too many FunctionTypes");

                bagFunction =
                    getFunction(node, xpathVersion,
                                FunctionFactory.getGeneralInstance());
            }
        }

        return new Apply(function, evals, bagFunction, isCondition);
    }

    /**
     * Helper method that tries to get a function instance
     */
    private static Function getFunction(Node root, String version,
                                        FunctionFactory factory)
        throws ParsingException
    {
        Node functionNode = root.getAttributes().getNamedItem("FunctionId");
        String functionName = functionNode.getNodeValue();

        try {
            // try to get an instance of the given function
            return factory.createFunction(functionName);
        } catch (UnknownIdentifierException uie) {
            throw new ParsingException("Unknown FunctionId in Apply", uie);
        } catch (FunctionTypeException fte) {
            // try creating as an abstract function, using a general factory
            try {
                FunctionFactory ff = FunctionFactory.getGeneralInstance();
                return ff.createAbstractFunction(functionName, root, version);
            } catch (Exception e) {
                // any exception at this point is a failure
                throw new ParsingException("failed to create abstract function"
                                           + " " + functionName, e);
            }
        }
    }

    /**
     * Returns the <code>Function</code> used by this <code>Apply</code>.
     *
     * @return the <code>Function</code>
     */
    public Function getFunction() {
        return function;
    }

    /**
     * Returns the <code>List</code> of children for this <code>Apply</code>.
     * The <code>List</code> contains <code>Evaluatable</code>s. The list is
     * unmodifiable, and may be empty.
     *
     * @return a <code>List</code> of <code>Evaluatable</code>s
     */
    public List getChildren() {
        return evals;
    }

    /**
     * Returns the higher order bag function used by this <code>Apply</code>
     * if it exists, or null if no higher order function is used.
     *
     * @return the higher order <code>Function</code> or null
     */
    public Function getHigherOrderFunction() {
        return bagFunction;
    }

    /**
     * Returns whether or not this ApplyType is actually a ConditionType.
     *
     * @return whether or not this represents a ConditionType
     */
    public boolean isCondition() {
        return isCondition;
    }

    /**
     * Evaluates the apply object using the given function. This will in
     * turn call evaluate on all the given parameters, some of which may be
     * other <code>Apply</code> objects.
     *
     * @param context the representation of the request
     *
     * @return the result of trying to evaluate this apply object
     */
    public EvaluationResult evaluate(EvaluationCtx context) {
        List parameters = evals;

        // see if there is a higher-order function in here
        if (bagFunction != null) {
            // this is a special case, so we setup the parameters, starting
            // with the function
            parameters = new ArrayList();
            parameters.add(bagFunction);

            // now we evaluate all the parameters, returning INDETERMINATE
            // if that's what any of them return, and otherwise tracking
            // all the AttributeValues that get returned
            Iterator it = evals.iterator();
            while (it.hasNext()) {
                Evaluatable eval = (Evaluatable)(it.next());
                EvaluationResult result = eval.evaluate(context);
                
                // in a higher-order case, if anything is INDETERMINATE, then
                // we stop right away
                if (result.indeterminate())
                    return result;

                parameters.add(result.getAttributeValue());
            }
        }

        // now we can call the base function
        return function.evaluate(parameters, context);
    }

    /**
     * Returns the type of attribute that this object will return on a call
     * to <code>evaluate</code>. In practice, this will always be the same as
     * the result of calling <code>getReturnType</code> on the function used
     * by this object.
     *
     * @return the type returned by <code>evaluate</code>
     */
    public URI getType() {
        return function.getReturnType();
    }

    /**
     * Returns whether or not the <code>Function</code> will return a bag
     * of values on evaluation.
     *
     * @return true if evaluation will return a bag of values, false otherwise
     */
    public boolean evaluatesToBag() {
        return function.returnsBag();
    }

    /**
     * Encodes this <code>Apply</code> into its XML representation and
     * writes this encoding to the given <code>OutputStream</code> with no
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     */
    public void encode(OutputStream output) {
        encode(output, new Indenter(0));
    }

    /**
     * Encodes this <code>Apply</code> into its XML representation and
     * writes this encoding to the given <code>OutputStream</code> with
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     * @param indenter an object that creates indentation strings
     */
    public void encode(OutputStream output, Indenter indenter) {
        PrintStream out = new PrintStream(output);
        String indent = indenter.makeString();

        if (isCondition)
            out.println(indent + "<Condition FunctionId=\"" +
                        function.getIdentifier() + "\">");
        else
            out.println(indent + "<Apply FunctionId=\"" +
                        function.getIdentifier() + "\">");
        indenter.in();

        if (bagFunction != null)
            out.println("<Function FunctionId=\"" +
                        bagFunction.getIdentifier() + "\"/>");

        Iterator it = evals.iterator();
        while (it.hasNext()) {
            Evaluatable eval = (Evaluatable)(it.next());
            eval.encode(output, indenter);
        }

        indenter.out();
        if (isCondition)
            out.println(indent + "</Condition>");
        else
            out.println(indent + "</Apply>");
    }

}
