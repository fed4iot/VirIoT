
/*
 * @(#)Target.java
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

import com.sun.xacml.ctx.Status;

import java.io.OutputStream;
import java.io.PrintStream;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import java.util.logging.Level;
import java.util.logging.Logger;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;


/**
 * Represents the TargetType XML type in XACML. This also stores several
 * other XML types: Subjects, Resources, and Actions. The target is 
 * used to quickly identify whether the parent element (a policy set, 
 * policy, or rule) is applicable to a given request. 
 *
 * @since 1.0
 * @author Seth Proctor
 */
public class Target
{

    // the elements in a Target, all of which are required
    private List subjects;
    private List resources;
    private List actions;

    // the logger we'll use for all messages
    private static final Logger logger =
        Logger.getLogger(Target.class.getName());

    /**
     * Constructor that creates a <code>Target</code> from components.
     *
     * @param subjects A <code>List</code> containing the subjects or null
     *                 if this represents AnySubject. The list is of the
     *                 form described in <code>getSubjects</code>.
     * @param resources A <code>List</code> containing the resources or null
     *                 if this represents AnyResource The list is of the
     *                 form described in <code>getResources</code>.
     * @param actions A <code>List</code> containing the actions or null
     *                 if this represents AnyAction The list is of the
     *                 form described in <code>getActions</code>.
     */
    public Target(List subjects, List resources, List actions) {
        if (subjects == null)
            this.subjects = subjects;
        else
            this.subjects = Collections.
                unmodifiableList(new ArrayList(subjects));

        if (resources == null)
            this.resources = resources;
        else
            this.resources = Collections.
                unmodifiableList(new ArrayList(resources));

        if (actions == null)
            this.actions = actions;
        else
            this.actions = Collections.
                unmodifiableList(new ArrayList(actions));
    }

    /**
     * Creates a <code>Target</code> by parsing a node.
     *
     * @param root the node to parse for the <code>Target</code>
     * @param xpathVersion the XPath version to use in any selectors, or
     *                     null if this is unspecified (ie, not supplied in
     *                     the defaults section of the policy)
     *
     * @return a new <code>Target</code> constructed by parsing
     *
     * @throws ParsingException if the DOM node is invalid
     */
    public static Target getInstance(Node root, String xpathVersion)
        throws ParsingException
    {
        List subjects = null;
        List resources = null;
        List actions = null;

        NodeList children = root.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            String name = child.getNodeName();

            if (name.equals("Subjects")) {
                subjects = getAttributes(child, "Subject", xpathVersion);
            } else if (name.equals("Resources")) {
                resources = getAttributes(child, "Resource", xpathVersion);
            } else if (name.equals("Actions")) {
                actions = getAttributes(child, "Action", xpathVersion);
            }
        }

        return new Target(subjects, resources, actions);
    }

    /**
     * Helper method that parses the contents of the Subjects,
     * Resources, or Actions types, depending on the input prefix,
     * which must be either "Subject", "Resource", or "Action".
     * A null List specifies any attributes will match; 
     * it represents AnySubject, AnyResource, or AnyAction.
     */
    private static List getAttributes(Node root, String prefix,
                                      String xpathVersion)
        throws ParsingException
    {
        List matches = new ArrayList();
        NodeList children = root.getChildNodes();

        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            String name = child.getNodeName();

            if (name.equals(prefix)) {
                matches.add(getMatches(child, prefix, xpathVersion));
            } else if (name.equals("Any" + prefix)) {
                return null;
            }
        }

        return matches;
    }

    /**
     * Helper method that parses the contents of a SubjectMatch,
     * ResourceMatch, or ActionMatch type, depending on the input
     * prefix, which must be either "Subject", "Resource" or "Action"
     */
    private static List getMatches(Node root, String prefix,
                                   String xpathVersion)
        throws ParsingException
    {
        List list = new ArrayList();
        NodeList children = root.getChildNodes();

        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            String name = child.getNodeName();

            if (name.equals(prefix + "Match"))
                list.add(TargetMatch.getInstance(child, prefix, xpathVersion));
        }

        return Collections.unmodifiableList(list);
    }

    /**
     * Returns an unmodifiable <code>List</code> that represents the Subjects
     * section of this target. Each entry in the <code>List</code> is
     * another <code>List</code> that represents the Subject section. In turn,
     * each of these <code>List</code>s contains <code>TargetMatch</code>
     * objects that represent SubjectMatch XML structures.
     * <p>
     * Note that future versions of this code may use intermediary classes to
     * make the structure clearer, but this depends on the future structure
     * of XACML Targets.
     *
     * @return the matching elements or null of the match is any
     */
    public List getSubjects() {
        return subjects;
    }

    /**
     * Returns an unmodifiable <code>List</code> that represents the Resources
     * section of this target. Each entry in the <code>List</code> is
     * another <code>List</code> that represents the Resource section. In turn,
     * each of these <code>List</code>s contains <code>TargetMatch</code>
     * objects that represent ResourceMatch XML structures.
     * <p>
     * Note that future versions of this code may use intermediary classes to
     * make the structure clearer, but this depends on the future structure
     * of XACML Targets.
     *
     * @return the matching elements or null of the match is any
     */
    public List getResources() {
        return resources;
    }

    /**
     * Returns an unmodifiable <code>List</code> that represents the Actions
     * section of this target. Each entry in the <code>List</code> is
     * another <code>List</code> that represents the Action section. In turn,
     * each of these <code>List</code>s contains <code>TargetMatch</code>
     * objects that represent ActionMatch XML structures.
     * <p>
     * Note that future versions of this code may use intermediary classes to
     * make the structure clearer, but this depends on the future structure
     * of XACML Targets.
     *
     * @return the matching elements or null of the match is any
     */
    public List getActions() {
        return actions;
    }

    /**
     * Determines whether this <code>Target</code> matches
     * the input request (whether it is applicable). 
     * 
     * @param context the representation of the request
     *
     * @return the result of trying to match the target and the request
     */
    public MatchResult match(EvaluationCtx context) {
        // first look to see if there are any subjects to match
        if (subjects != null) {
            MatchResult result = checkSet(subjects, context);
            if (result.getResult() != MatchResult.MATCH) {
                logger.finer("failed to match Subjects section of Target");
                return result;
            }
        }

        // now look to see if there is a resource to match
        if (resources != null) {
            MatchResult result = checkSet(resources, context);
            if (result.getResult() != MatchResult.MATCH) {
                logger.finer("failed to match Resources section of Target");
                return result;
            }
        }

        // finally, see if there are any actions to match
        if (actions != null) {
            MatchResult result = checkSet(actions, context);
            if (result.getResult() != MatchResult.MATCH) {
                logger.finer("failed to match Actions section of Target");
                return result;
            }
        }

        // if we got here, then everything matched
        return new MatchResult(MatchResult.MATCH);
    }

    /**
     * Helper function that determines whether there is at least
     * one positive match between each section of the Target element
     * and the input request
     */
    private MatchResult checkSet(List matchList, EvaluationCtx context) {
        Iterator it = matchList.iterator();
        boolean allFalse = true;
        Status firstIndeterminateStatus = null;

        // for each item in this loop, there must be at least one match 
        while (it.hasNext()) {
            // first off, get the next set of objects
            List list = (List)(it.next());
            Iterator it2 = list.iterator();
            MatchResult result = null;

            // now we go through the set, every one of which must match
            while (it2.hasNext()) {
                TargetMatch tm = (TargetMatch)(it2.next());
                result = tm.match(context);
                if (result.getResult() != MatchResult.MATCH)
                    break;
            }

            // if the last one was a MATCH, then all of the matches
            // matched, so we're done 
            if (result.getResult() == MatchResult.MATCH)
                return result;

            // if we didn't match then it was either a NO_MATCH or
            // INDETERMINATE...in the second case, we need to remember
            // it happened, 'cause if we don't get a MATCH, then we'll
            // be returning INDETERMINATE
            if (result.getResult() == MatchResult.INDETERMINATE) {
                allFalse = false;

                if (firstIndeterminateStatus == null)
                    firstIndeterminateStatus = result.getStatus();
            }
        }

        // if we got here, then none of the sub-matches passed, so
        // we have to see if we got any INDETERMINATE cases
        if (allFalse)
            return new MatchResult(MatchResult.NO_MATCH);
        else
            return new MatchResult(MatchResult.INDETERMINATE,
                                   firstIndeterminateStatus);
    }

    /**
     * Encodes this <code>Target</code> into its XML representation and writes
     * this encoding to the given <code>OutputStream</code> with no
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     */
    public void encode(OutputStream output) {
        encode(output, new Indenter(0));
    }

    /**
     * Encodes this <code>Target</code> into its XML representation and writes
     * this encoding to the given <code>OutputStream</code> with
     * indentation.
     *
     * @param output a stream into which the XML-encoded data is written
     * @param indenter an object that creates indentation strings
     */
    public void encode(OutputStream output, Indenter indenter) {
        PrintStream out = new PrintStream(output);
        String indent = indenter.makeString();

        out.println(indent + "<Target>");
        indenter.in();
        
        encodeSection(out, indenter, "Subject", subjects);
        encodeSection(out, indenter, "Resource", resources);
        encodeSection(out, indenter, "Action", actions);

        indenter.out();
        out.println(indent + "</Target>");
    }

    /**
     * Helper function that encodes a section of the target.
     */
    private void encodeSection(PrintStream output, Indenter indenter,
                               String name, List list) {
        String indent = indenter.makeString();

        output.println(indent + "<" + name + "s>");

        indenter.in();
        String indentNext = indenter.makeString();

        if (list == null) {
            // the match is any
            output.println(indentNext + "<Any" + name + "/>");
        } else {
            String nextIndent = indenter.makeString();

            Iterator it = list.iterator();
            indenter.in();

            while (it.hasNext()) {
                List items = (List)(it.next());
                output.println(indentNext + "<" + name + ">");
                
                Iterator matchIterator = items.iterator();
                while (matchIterator.hasNext()) {
                    TargetMatch tm = (TargetMatch)(matchIterator.next());
                    tm.encode(output, indenter);
                }

                output.println(indentNext + "</" + name + ">");
            }

            indenter.out();
        }

        indenter.out();
        output.println(indent + "</" + name + "s>");
    }

}
