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
package umu.xacml.webpap;

import Umu_xacml_util.Umu_xacml_util;
import xacmleditor.ElementoObligation;

/**
 * This class represents an XACML Obligation element.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class Obligation {

    private String id;
    private Fulfill fulFillOn;

    /**
     * Creates a new obligation with the given id.
     * @param id the id of the obligation.
     */
    Obligation(String id) {
        this.id = id;
        fulFillOn = Fulfill.Permit;
    }

    /**
     * Creates a new instance using an obligation element of the XACML Editor library.
     * @param umu_xacml_util utility object to be used.
     * @param elementoObligation the obligation element.
     */
    Obligation(Umu_xacml_util umu_xacml_util, ElementoObligation elementoObligation) {
        id = (String) elementoObligation.getAtributos().get("ObligationId");
        String sFulfillOn = (String) elementoObligation.getAtributos().get("FulfillOn");
        if (sFulfillOn.equals("Permit")) {
            fulFillOn = Fulfill.Permit;
        } else if (sFulfillOn.equals("Deny")) {
            fulFillOn = Fulfill.Deny;
        }
    }

    /**
     * FulfillOn attribute values.
     */
    public enum Fulfill {

        /**
         * Permit value for FulfillOn attribute.
         */
        Permit,
        /**
         * Deny value for FulfillOn attribute.
         */
        Deny
    };

    /**
     * Returns the id of the obligation.
     * @return the id of the obligation.
     */
    public String getId() {
        return id;
    }

    /**
     * Sets the id of the obligation.
     * @param id the id of the obligation.
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * Returns the FullfillOn attribute of the obligation.
     * @return the FullfillOn attribute.
     */
    public Fulfill getFulFillOn() {
        return fulFillOn;
    }

    /**
     * Sets the FullfillOn attribute of the obligation.
     * @param FulFillOn the FullfillOn attribute.
     */
    public void setFulFillOn(Fulfill FulFillOn) {
        this.fulFillOn = FulFillOn;
    }

    /**
     * Returns the utility object for this action.
     * @return the utility object of the action.
     */
    public Umu_xacml_util getUMU_XACML() {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
        ElementoObligation elementoObligation = (ElementoObligation) umu_xacml_util.createPrincipal(ElementoObligation.TIPO_OBLIGATION);
        elementoObligation.getAtributos().put("ObligationId", id);
        if (fulFillOn.equals(Fulfill.Permit)) {
            elementoObligation.getAtributos().put("FulfillOn", "Permit");
        } else {
            elementoObligation.getAtributos().put("FulfillOn", "Deny");
        }
        return umu_xacml_util;
    }
}
