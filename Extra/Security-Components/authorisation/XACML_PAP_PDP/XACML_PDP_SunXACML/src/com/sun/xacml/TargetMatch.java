
/*
 * @(#)TargetMatch.java
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

import com.sun.xacml.EvaluationCtx;

import com.sun.xacml.attr.AttributeDesignator;
import com.sun.xacml.attr.AttributeFactory;
import com.sun.xacml.attr.AttributeSelector;
import com.sun.xacml.attr.AttributeValue;
import com.sun.xacml.attr.BagAttribute;
import com.sun.xacml.attr.BooleanAttribute;

import com.sun.xacml.cond.Evaluatable;
import com.sun.xacml.cond.EvaluationResult;
import com.sun.xacml.cond.Function;
import com.sun.xacml.cond.FunctionFactory;
import com.sun.xacml.cond.FunctionTypeException;

import com.sun.xacml.ctx.Status;

import java.io.OutputStream;
import java.io.PrintStream;

import java.net.URI;
import java.net.URISyntaxException;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;


/**
 * Represents the SubjectMatch, ResourceMatch, or ActionMatch XML types in
 * XACML, depending on the value of the type field. This is the part of the 
 * Target that actually evaluates whether the specified attribute values in the
 * Target match the corresponding attribute values in the request context.
 *
 * @since 1.0
 * @author Seth Proctor
 */
public class TargetMatch
{

    /**
     * An integer value indicating that this class represents a SubjectMatch
     */
    public static final int SUBJECT = 0;

    /**
     * An integer value indicating that this class represents a ResourceMatch
     */
    public static final int RESOURCE = 1;

    /**
     * An integer value indicating that this class represents an ActionMatch
     */
    public static final int ACTION = 2;

    //
    private int type;
    private Function function;
    private Evaluatable eval;
    private AttributeValue attrValue;

    /**
     * Constructor that creates a <code>TargetMatch</code> from components.
     *
     * @param type an integer indicating whether this class represents a
     *             SubjectMatch, ResourceMatch, or ActionMatch
     * @param function the <code>Function</code> that represents the MatchId
     * @param eval the <code>AttributeDesignator</code> or 
     *             <code>AttributeSelector</code> to be used to select 
     *             attributes from the request context
     * @param attrValue the <code>AttributeValue</code> to compare against
     *
     * @throws IllegalArgumentException if the input type isn't a valid value
     */
    public TargetMatch(int type, Function function, Evaluatable eval,
                       AttributeValue attrValue) 
        throws IllegalArgumentException {

        // check if input type is a valid value
        if ((type != SUBJECT) && 
            (type != RESOURCE) &&
            (type != ACTION))
            throw new IllegalArgumentException("Unknown TargetMatch type");

        this.type = type;
        this.function = function;
        this.eval = eval;
        this.attrValue = attrValue;
    }

    /**
     * Creates a <code>TargetMatch</code> by parsing a node, using the
     * input prefix to determine whether this is a SubjectMatch, ResourceMatch,
     * or ActionMatch.
     *
     * @param root the node to parse for the <code>TargetMatch</code>
     * @param prefix a String indicating what type of <code>TargetMatch</code>
     *               to instantiate (Subject, Resource, or Action)
     * @param xpathVersion the XPath version to use in any selectors, or
     *                     null if this is unspecified (ie, not supplied in
     *                     the defaults section of the policy)
     * 
     * @return a new <code>TargetMatch</code> constructed by parsing
     *
     * @throws ParsingException if there was an error during parsing
     * @throws IllegalArgumentException if the input prefix isn't a valid value
     */
    public static TargetMatch getInstance(Node root, String prefix,
                                          String xpathVersion)
        throws ParsingException, IllegalArgumentException
    {
        int type;
        Function function;
        Evaluatable eval = null;
        AttributeValue attrValue = null;

        AttributeFactory attrFactory = AttributeFactory.getInstance();

        // first off, figure out which of three types we are
        if (prefix.equals("Subject")) {
            type = SUBJECT;
        } else if (prefix.equals("Resource")) {
            type = RESOURCE;
        } else if (prefix.equals("Action")) {
            type = ACTION;
        } else {
            throw new IllegalArgumentException("Unknown TargetMatch type");
        }

        // now get the function type, making sure that it's really a correct
        // Target function
        String funcName = root.getAttributes().
            getNamedItem("MatchId").getNodeValue();
        FunctionFactory factory = FunctionFactory.getTargetInstance();
        try {
            URI funcId = new URI(funcName);
            function = factory.createFunction(funcId);
        } catch (URISyntaxException use) {
            throw new ParsingException("Error parsing TargetMatch", use);
        } catch (UnknownIdentifierException uie) {
            throw new ParsingException("Unknown MatchId", uie);
        } catch (FunctionTypeException fte) {
            // try to create an abstract function
            try {
                URI funcId = new URI(funcName);
                function = factory.createAbstractFunction(funcId, root);
            } catch (Exception e) {
                // any exception here is an error
                throw new ParsingException("invalid abstract function", e);
            }
        }

        // next, get the designator or selector being used, and the attribute
        // value paired with it
        NodeList nodes = root.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            String name = node.getNodeName();

            if (name.equals(prefix + "AttributeDesignator")) {
                eval = AttributeDesignator.getInstance(node, type);
            } else if (name.equals("AttributeSelector")) {
                eval = AttributeSelector.getInstance(node, xpathVersion);
            } else if (name.equals("AttributeValue")) {
                try {
                    attrValue = attrFactory.createValue(node);
                } catch (UnknownIdentifierException uie) {
                    throw new ParsingException("Unknown Attribute Type", uie);
                }
            }
        }

        // finally, check that the inputs are valid for this function
        List inputs = new ArrayList();
        inputs.add(attrValue);
        inputs.add(eval);
        function.checkInputsNoBag(inputs);

        return new TargetMatch(type, function, eval, attrValue);
    }

    /**
     * Returns the type of this <code>TargetMatch</code>, either
     * <code>SUBJECT</code>, <code>RESOURCE</code>, or <code>ACTION</code>.
     *
     * @return the type
     */
    public int getType() {
        return type;
    }

    /**
     * Returns the <code>Function</code> used to do the matching.
     *
     * @return the match function
     */
    public Function getMatchFunction() {
        return function;
    }

    /**
     * Returns the <code>AttributeValue</code> used by the matching function.
     *
     * @return the <code>AttributeValue</code> for the match
     */
    public AttributeValue getMatchValue() {
        return attrValue;
    }

    /**
     * Returns the <code>AttributeDesignator</code> or
     * <code>AttributeSelector</code> used by the matching function.
     *
     * @return the designator or selector for the match
     */
    public Evaluatable getMatchEvaluatable() {
        return eval;
    }

    /**
     * Determines whether this <code>TargetMatch</code> matches
     * the input request (whether it is applicable)
     *
     * @param context the representation of the request
     *
     * @return the result of trying to match the TargetMatch and the request
     */
    public MatchResult match(EvaluationCtx context) {
        // start by evaluating the AD/AS
        EvaluationResult result = eval.evaluate(context);
        
        if (result.indeterminate()) {
            // in this case, we don't ask the function for anything, and we
            // simply return INDETERMINATE
            return new MatchResult(MatchResult.INDETERMINATE,
                                   result.getStatus());
        }

        // an AD/AS will always return a bag
        BagAttribute bag = (BagAttribute)(result.getAttributeValue());

        if (! bag.isEmpty()) {
            // we got back a set of attributes, so we need to iterate through
            // them, seeing if at least one matches
            Iterator it = bag.iterator();
            boolean atLeastOneError = false;
            Status firstIndeterminateStatus = null;

            while (it.hasNext()) {
                ArrayList inputs = new ArrayList();

                inputs.add(attrValue);
                inputs.add(it.next());

                // do the evaluation
                MatchResult match = evaluateMatch(inputs, context);
                
                // we only need one match for this whole thing to match
                if (match.getResult() == MatchResult.MATCH)
                    return match;

                // if it was INDETERMINATE, we want to remember for later
                if (match.getResult() == MatchResult.INDETERMINATE) {
                    atLeastOneError = true;

                    // there are no rules about exactly what status data
                    // should be returned here, so like in the combining
                    // algs, we'll just track the first error
                    if (firstIndeterminateStatus == null)
                        firstIndeterminateStatus = match.getStatus();
                }
            }

            // if we got here, then nothing matched, so we'll either return
            // INDETERMINATE or NO_MATCH
            if (atLeastOneError)
                return new MatchResult(MatchResult.INDETERMINATE,
                                       firstIndeterminateStatus);
            else
                return new MatchResult(MatchResult.NO_MATCH);

        } else {
            // this is just an optimization, since the loop above will
            // actually handle this case, but this is just a little
            // quicker way to handle an empty bag
            return new MatchResult(MatchResult.NO_MATCH);
        }
    }
    
    /**
     * Private helper that evaluates an individual match.
     */
    private MatchResult evaluateMatch(List inputs, EvaluationCtx context) {
        // first off, evaluate the function
        EvaluationResult result = function.evaluate(inputs, context);

        // if it was indeterminate, then that's what we return immediately
        if (result.indeterminate())
            return new MatchResult(MatchResult.INDETERMINATE,
                                   result.getStatus());

        // otherwise, we figure out if it was a match
        BooleanAttribute bool = (BooleanAttribute)(result.getAttributeValue());

        if (bool.getValue())
            return new MatchResult(MatchResult.MATCH);
        else
            return new MatchResult(MatchResult.NO_MATCH);
    }

    /**
     * Encodes this <code>TargetMatch</code> into its XML representation and
     * writes this encoding to the given <code>OutputStream</code> with no
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     */
    public void encode(OutputStream output) {
        encode(output, new Indenter(0));
    }

    /**
     * Encodes this <code>TargetMatch</code> into its XML representation and
     * writes this encoding to the given <code>OutputStream</code> with
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     * @param indenter an object that creates indentation strings
     */
    public void encode(OutputStream output, Indenter indenter) {
        PrintStream out = new PrintStream(output);
        String indent = indenter.makeString();
        String tagName = null;

        switch (type) {
        case SUBJECT: tagName = "SubjectMatch";
            break;
        case RESOURCE: tagName = "ResourceMatch";
            break;
        case ACTION: tagName = "ActionMatch";
            break;
        }

        out.println(indent + "<" + tagName + " MatchId=\"" +
                    function.getIdentifier().toString()+ "\">");
        indenter.in();

        attrValue.encode(output, indenter);
        eval.encode(output, indenter);
        
        indenter.out();
        out.println(indent + "</" + tagName + ">");
    }

}
