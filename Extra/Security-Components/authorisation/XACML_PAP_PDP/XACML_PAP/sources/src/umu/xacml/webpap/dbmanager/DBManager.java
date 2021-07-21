/*
 *    Copyright (C) 2012, 2013 Universidad de Murcia
 *
 *    Authors:
 *        Ginés Dólera Tormo <ginesdt@um.es>
 *        Juan M. Marín Pérez <juanmanuel@um.es>
 *        Jorge Bernal Bernabé <jorgebernal@um.es>
 *        Gregorio Martínez Pérez <gregorio@um.es>
 *        Antonio F. Skarmeta Gómez <skarmeta@um.es>
 *		  Dan García Carrillo <dan.garcia@um.es>
 *
 *    This file is part of XACML Web Policy Administration Point (XACML-WebPAP).
 *
 *    XACML-WebPAP is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Lesser General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    XACML-WebPAP is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *    GNU Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public License
 *    along with XACML-WebPAP. If not, see <http://www.gnu.org/licenses/>.
 * 
 */
package umu.xacml.webpap.dbmanager;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import umu.xacml.webpap.Resource;
import umu.xacml.webpap.Subject;
import umu.xacml.webpap.XACMLAttributeElement;

/**
 * This interface represents a database manager providing data access methods.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public interface DBManager {

     /**
     * Retrieves the policy set.
     * @return the policy set.
     */
    public String retrievePolicySet();

    /**
     * Store a policy set.
     * @param policySet the policy set.
     */
    public void storePolicySet(String policySet);

    void storeXACMLAttributes(List<XACMLAttributeElement> attributes) throws IOException;

    public List<XACMLAttributeElement> getXACMLAttributes() throws IOException;
    
}
