
/*
 * @(#)StandardAttributeFactory
 *
 * Copyright 2004 Sun Microsystems, Inc. All Rights Reserved.
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

package com.sun.xacml.attr;

import com.sun.xacml.attr.proxy.AnyURIAttributeProxy;
import com.sun.xacml.attr.proxy.Base64BinaryAttributeProxy;
import com.sun.xacml.attr.proxy.BooleanAttributeProxy;
import com.sun.xacml.attr.proxy.DateAttributeProxy;
import com.sun.xacml.attr.proxy.DateTimeAttributeProxy;
import com.sun.xacml.attr.proxy.DayTimeDurationAttributeProxy;
import com.sun.xacml.attr.proxy.DoubleAttributeProxy;
import com.sun.xacml.attr.proxy.HexBinaryAttributeProxy;
import com.sun.xacml.attr.proxy.IntegerAttributeProxy;
import com.sun.xacml.attr.proxy.RFC822NameAttributeProxy;
import com.sun.xacml.attr.proxy.StringAttributeProxy;
import com.sun.xacml.attr.proxy.TimeAttributeProxy;
import com.sun.xacml.attr.proxy.YearMonthDurationAttributeProxy;
import com.sun.xacml.attr.proxy.X500NameAttributeProxy;

import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import java.util.logging.Logger;

import org.w3c.dom.Node;


/**
 * This factory supports the standard set of datatypes specified in XACML
 * 1.0 and 1.1. It is the default factory used by the system, and imposes
 * a singleton pattern insuring that there is only ever one instance of
 * this class.
 * <p>
 * Note that because this supports only the standard datatypes, this
 * factory does not allow the addition of any other datatypes. If you call
 * <code>addDatatype</code> on an instance of this class, an exception
 * will be thrown. If you need a standard factory that is modifiable, you
 * should create a new <code>BaseAttributeFactory</code> (or some other
 * <code>AttributeFactory</code>) and configure it with the standard
 * datatypes using <code>addStandardDatatypes</code> (or, in the case of
 * <code>BaseAttributeFactory</code>, by providing the datatypes in the
 * constructor).
 *
 * @since 1.2
 * @author Seth Proctor
 */
public class StandardAttributeFactory extends BaseAttributeFactory
{

    // the one instance of this factory
    private static StandardAttributeFactory factoryInstance = null;

    // the datatypes supported by this factory
    private static Map supportedDatatypes = null;

    // the logger we'll use for all messages
    private static final Logger logger =
        Logger.getLogger(StandardAttributeFactory.class.getName());

    /**
     * Private constructor that sets up proxies for all of the standard
     * datatypes.
     */
    private StandardAttributeFactory() {
        super(supportedDatatypes);
    }

    /**
     * Private initializer for the supported datatypes. This isn't called
     * until something needs these values, and is only called once.
     */
    private static void initDatatypes() {
        logger.config("Initializing standard datatypes");

        supportedDatatypes = new HashMap();

        supportedDatatypes.put(BooleanAttribute.identifier,
                               new BooleanAttributeProxy());
        supportedDatatypes.put(StringAttribute.identifier,
                               new StringAttributeProxy());
        supportedDatatypes.put(DateAttribute.identifier,
                               new DateAttributeProxy());
        supportedDatatypes.put(TimeAttribute.identifier,
                               new TimeAttributeProxy());
        supportedDatatypes.put(DateTimeAttribute.identifier,
                               new DateTimeAttributeProxy());
        supportedDatatypes.put(DayTimeDurationAttribute.identifier,
                               new DayTimeDurationAttributeProxy());
        supportedDatatypes.put(YearMonthDurationAttribute.identifier,
                               new YearMonthDurationAttributeProxy());
        supportedDatatypes.put(DoubleAttribute.identifier,
                               new DoubleAttributeProxy());
        supportedDatatypes.put(IntegerAttribute.identifier,
                               new IntegerAttributeProxy());
        supportedDatatypes.put(AnyURIAttribute.identifier,
                               new AnyURIAttributeProxy());
        supportedDatatypes.put(HexBinaryAttribute.identifier,
                               new HexBinaryAttributeProxy());
        supportedDatatypes.put(Base64BinaryAttribute.identifier,
                               new Base64BinaryAttributeProxy());
        supportedDatatypes.put(X500NameAttribute.identifier,
                               new X500NameAttributeProxy());
        supportedDatatypes.put(RFC822NameAttribute.identifier,
                               new RFC822NameAttributeProxy());
    }

    /**
     * Returns an instance of this factory. This method enforces a singleton
     * model, meaning that this always returns the same instance, creating
     * the factory if it hasn't been requested before. This is the default
     * model used by the <code>AttributeFactory</code>, ensuring quick
     * access to this factory.
     *
     * @return the factory instance
     */
    public static StandardAttributeFactory getFactory() {
        if (factoryInstance == null) {
            synchronized (StandardAttributeFactory.class) {
                if (factoryInstance == null) {
                    initDatatypes();
                    factoryInstance = new StandardAttributeFactory();
                }
            }
        }

        return factoryInstance;
    }

    /**
     * Returns the set of datatypes that this standard factory supports.
     *
     * @return a <code>Map</code> of <code>String</code> to
     *         <code>AttributeProxy</code>s
     */
    public Map getStandardDatatypes() {
        return Collections.unmodifiableMap(supportedDatatypes);
    }

    /**
     * Throws an <code>UnsupportedOperationException</code> since you are not
     * allowed to modify what a standard factory supports.
     *
     * @param id the name of the attribute type
     * @param proxy the proxy used to create new attributes of the given type
     *
     * @throws UnsupportedOperationException always
     */
    public void addDatatype(String id, AttributeProxy proxy) {
        throw new UnsupportedOperationException("a standard factory cannot " +
                                                "support new datatypes");
    }

}
