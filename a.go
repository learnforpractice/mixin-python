func signTransactionCmd(c *cli.Context) error {
	var raw signerInput
	err := json.Unmarshal([]byte(c.String("raw")), &raw)
	if err != nil {
		return err
	}
	raw.Node = c.String("node")

	seed, err := hex.DecodeString(c.String("seed"))
	if err != nil {
		return err
	}
	if len(seed) != 64 {
		seed = make([]byte, 64)
		_, err := rand.Read(seed)
		if err != nil {
			return err
		}
	}

	tx := common.NewTransaction(raw.Asset)
	for _, in := range raw.Inputs {
		if d := in.Deposit; d != nil {
			tx.AddDepositInput(&common.DepositData{
				Chain:           d.Chain,
				AssetKey:        d.AssetKey,
				TransactionHash: d.TransactionHash,
				OutputIndex:     d.OutputIndex,
				Amount:          d.Amount,
			})
		} else {
			tx.AddInput(in.Hash, in.Index)
		}
	}

	for _, out := range raw.Outputs {
		if out.Mask.HasValue() {
			tx.Outputs = append(tx.Outputs, &common.Output{
				Type:   out.Type,
				Amount: out.Amount,
				Keys:   out.Keys,
				Script: out.Script,
				Mask:   out.Mask,
			})
		} else {
			hash := crypto.NewHash(seed)
			seed = append(hash[:], hash[:]...)
			tx.AddOutputWithType(out.Type, out.Accounts, out.Script, out.Amount, seed)
		}
	}

	extra, err := hex.DecodeString(raw.Extra)
	if err != nil {
		return err
	}
	tx.Extra = extra

	keys := c.StringSlice("key")
	var accounts []*common.Address
	for _, s := range keys {
		key, err := hex.DecodeString(s)
		if err != nil {
			return err
		}
		if len(key) != 64 {
			return fmt.Errorf("invalid key length %d", len(key))
		}
		var account common.Address
		copy(account.PrivateViewKey[:], key[:32])
		copy(account.PrivateSpendKey[:], key[32:])
		accounts = append(accounts, &account)
	}

	signed := tx.AsLatestVersion()
	for i := range signed.Inputs {
		err := signed.SignInput(raw, i, accounts)
		if err != nil {
			return err
		}
	}
	fmt.Println(hex.EncodeToString(signed.Marshal()))
	return nil
}
